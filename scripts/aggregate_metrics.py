"""
Periodic Cognitive Telemetry Aggregator.
Reads anonymous metrics.json and computes population-level cognitive statistics.
Ref: 27-TELEMETRY-LOGGING-AND-ERROR-TAXONOMY.md.
"""

from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from collections import Counter
import numpy as np


def aggregate_telemetry():
    base_dir = Path(__file__).resolve().parent.parent / "services" / "core-engine" / "telemetry"
    metrics_file = base_dir / "metrics.json"
    summary_file = base_dir / "aggregated_summary.json"

    if not metrics_file.exists():
        print(f"Telemetri dosyası henüz oluşturulmadı: {metrics_file}")
        return

    records = []
    with open(metrics_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue

    if not records:
        print("İşlenecek telemetri kaydı bulunamadı.")
        return

    total_events = len(records)
    correct_events = sum(1 for r in records if r.get("is_correct"))
    accuracy = (correct_events / total_events) * 100.0

    latencies = [r.get("latency_ms", 0.0) for r in records if r.get("latency_ms") is not None]
    p95_latency = float(np.percentile(latencies, 95)) if latencies else 0.0
    mean_latency = float(np.mean(latencies)) if latencies else 0.0

    drift_rates = [r.get("ddm_drift_v") for r in records if r.get("ddm_drift_v") is not None]
    mean_drift = float(np.mean(drift_rates)) if drift_rates else None

    boundaries = [r.get("ddm_boundary_a") for r in records if r.get("ddm_boundary_a") is not None]
    mean_boundary = float(np.mean(boundaries)) if boundaries else None

    affective_states = Counter(r.get("affective_state", "UNKNOWN") for r in records)
    circuit_trips = sum(1 for r in records if r.get("circuit_breaker_tripped"))

    bugs = Counter(r.get("detected_bug_id") for r in records if r.get("detected_bug_id"))

    summary = {
        "total_steps_recorded": total_events,
        "overall_accuracy_percent": round(accuracy, 2),
        "mean_latency_ms": round(mean_latency, 2),
        "p95_latency_ms": round(p95_latency, 2),
        "mean_ddm_drift_v": round(mean_drift, 4) if mean_drift is not None else None,
        "mean_ddm_boundary_a": round(mean_boundary, 4) if mean_boundary is not None else None,
        "circuit_breaker_trips_count": circuit_trips,
        "circuit_breaker_trip_rate_percent": round((circuit_trips / total_events) * 100.0, 2),
        "affective_state_distribution": dict(affective_states),
        "top_misconceptions": dict(bugs.most_common(5)),
    }

    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("==========================================================")
    print(" BİLİŞSEL TELEMETRİ TOPLULAŞTIRMA ÖZETİ")
    print("==========================================================")
    print(f"Toplam Kayıtlı Adım Sayısı:      {total_events}")
    print(f"Genel Doğruluk Oranı:            %{accuracy:.2f}")
    print(f"Ortalama Adım Gecikmesi:         {mean_latency:.2f} ms")
    print(f"P95 Adım Gecikmesi:              {p95_latency:.2f} ms")
    print(f"Ortalama DDM Sürüklenme Hızı (v):{mean_drift}")
    print(f"Afektif Şalter Tetiklenme Sayısı:{circuit_trips} (%{(circuit_trips/total_events)*100:.2f})")
    print(f"Duygudurum Dağılımı:             {dict(affective_states)}")
    print(f"En Sık Görülen Bozuk Kurallar:   {dict(bugs)}")
    print(f"Rapor Kaydedildi:                {summary_file}")
    print("==========================================================")


if __name__ == "__main__":
    aggregate_telemetry()
