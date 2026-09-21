"""
Structured JSON Logging & Standardized Error Taxonomy (1000-4999).
Ref: 27-TELEMETRY-LOGGING-AND-ERROR-TAXONOMY.md.
"""

from __future__ import annotations
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any


# ====================================================================
# Standart Sistem Hata Kodları Kataloğu (Error Code Taxonomy 1000-4999)
# ====================================================================
class ErrorTaxonomy:
    # 2.1. Sembolik Matematik ve CAS Hataları (1000-1999)
    ERR_CAS_PARSE_FAILED = 1001
    ERR_CAS_DEPTH_EXCEEDED = 1002
    ERR_CAS_TIMEOUT = 1003
    ERR_CAS_DIVISION_BY_ZERO = 1004
    ERR_CAS_INVALID_CHARACTERS = 1005

    # 2.2. Bilgi Grafı ve DAG Hataları (2000-2999)
    ERR_DAG_NODE_NOT_FOUND = 2001
    ERR_DAG_CYCLE_DETECTED = 2002
    ERR_DAG_PREREQUISITE_LOCKED = 2003

    # 2.3. Bilişsel Model ve Psikometri Hataları (3000-3999)
    ERR_BKT_CONVERGENCE_FAILED = 3001
    ERR_DDM_DEGENERATE_DATA = 3002
    ERR_CAT_ITEM_EXHAUSTED = 3003

    # 2.4. Güvenlik, LLM ve Sokratik Hatalar (4000-4999)
    ERR_SEC_ZERO_LEAK_TRIGGERED = 4001
    ERR_SEC_RATE_LIMIT_EXCEEDED = 4002
    ERR_SEC_UNAUTHORIZED_TOKEN = 4003


class JsonLogFormatter(logging.Formatter):
    """
    OpenTelemetry & ELK uyumlu yapılandırılmış JSON loglayıcı.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Extra alanlar varsa ekle
        if hasattr(record, "error_code"):
            log_obj["error_code"] = record.error_code
        if hasattr(record, "trace_id"):
            log_obj["trace_id"] = record.trace_id
        if hasattr(record, "session_id"):
            log_obj["session_id"] = record.session_id
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms
        if hasattr(record, "status_code"):
            log_obj["status_code"] = record.status_code
        if hasattr(record, "client_ip"):
            log_obj["client_ip"] = record.client_ip

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


def setup_logging(log_level: str = "INFO") -> None:
    """Yapılandırılmış JSON loglayıcıyı kök seviyede yapılandırır."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    # Mevcut handler'ları temizle ve JSON handler ekle
    root_logger.handlers.clear()
    root_logger.addHandler(handler)


# ====================================================================
# Bilişsel Telemetri Toplayıcı (Anonymous Cognitive Metrics Recorder)
# ====================================================================
class CognitiveTelemetryLogger:
    """
    Öğrenci adım kayıtları, DDM sürüklenme hızı ve afektif durumları
    anonimleştirilmiş JSON çizgileri halinde saklar.
    """

    def __init__(self, metrics_filepath: Optional[Path] = None):
        if metrics_filepath is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            telemetry_dir = base_dir / "telemetry"
            telemetry_dir.mkdir(exist_ok=True)
            self.filepath = telemetry_dir / "metrics.json"
        else:
            self.filepath = metrics_filepath

    def record_step_event(
        self,
        session_id: str,
        step_index: int,
        is_correct: bool,
        latency_ms: float,
        ddm_v: Optional[float] = None,
        ddm_a: Optional[float] = None,
        affective_state: Optional[str] = None,
        circuit_breaker_tripped: bool = False,
        detected_bug_id: Optional[str] = None,
    ) -> None:
        """Adım bazlı telemetri kaydını atomik olarak dosyaya ekler."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id,
            "step_index": step_index,
            "is_correct": is_correct,
            "latency_ms": round(latency_ms, 2),
            "ddm_drift_v": round(ddm_v, 4) if ddm_v is not None else None,
            "ddm_boundary_a": round(ddm_a, 4) if ddm_a is not None else None,
            "affective_state": affective_state or "FLOW",
            "circuit_breaker_tripped": circuit_breaker_tripped,
            "detected_bug_id": detected_bug_id,
        }

        try:
            with open(self.filepath, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            logging.getLogger("telemetry").error(f"Telemetri yazma hatası: {e}")


telemetry_logger = CognitiveTelemetryLogger()
