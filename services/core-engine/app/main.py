from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.endpoints import router as session_router
from app.focus_domain.api import install_focus_api

# Yapılandırılmış JSON Loglama Kurulumu
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="Kişisel Öğrenme Motoru - CAS & Bilişsel Çekirdek Servisi",
    version="1.0.0",
    description="Nöro-Sembolik Adaptif Öğrenme Sistemi Çekirdek API",
    debug=settings.DEBUG,
)

import uuid
import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.core.logging_config import ErrorTaxonomy

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.trace_id = trace_id
        start_time = time.perf_counter()

        logger = logging.getLogger("core-engine.http")
        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            response.headers["X-Request-ID"] = trace_id
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
                extra={
                    "trace_id": trace_id,
                    "duration_ms": duration_ms,
                    "status_code": response.status_code,
                },
            )
            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                f"Unhandled Exception on {request.method} {request.url.path}: {exc}",
                exc_info=True,
                extra={
                    "trace_id": trace_id,
                    "duration_ms": duration_ms,
                    "error_code": ErrorTaxonomy.ERR_CAS_PARSE_FAILED if "SympifyError" in type(exc).__name__ else 5000,
                },
            )
            raise

from starlette.responses import JSONResponse

MAX_PAYLOAD_SIZE_BYTES = 10 * 1024  # 10 KB (Aşama 53)

class PayloadSizeLimitMiddleware(BaseHTTPMiddleware):
    """
    Aşama 53: Anormal büyük girdi gövdelerini (10KB üzeri) doğrudan reddeder.
    """
    async def dispatch(self, request: Request, call_next):
        if request.method in ("POST", "PUT", "PATCH"):
            content_length = request.headers.get("content-length")
            if content_length:
                try:
                    if int(content_length) > MAX_PAYLOAD_SIZE_BYTES:
                        return JSONResponse(
                            status_code=413,
                            content={"detail": "Payload Too Large: Maksimum istek boyutu 10KB sınırını aştı."},
                        )
                except ValueError:
                    pass
        return await call_next(request)

# Sıkılaştırılmış CORS ve Güvenlik ayarları (app/core/config.py ve .env kaynaklı)
app.add_middleware(PayloadSizeLimitMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(session_router)

# Focus V1 Alpha is isolated behind a default-off feature flag.
# When disabled, no /focus/v1 routes are registered.
install_focus_api(
    app,
    enabled=settings.FOCUS_V1_ENABLED,
    canary_percentage=settings.FOCUS_CANARY_PERCENTAGE,
    kill_switch=settings.FOCUS_KILL_SWITCH,
)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "core-engine",
        "environment": settings.ENVIRONMENT,
        "cas_status": "ready",
        "focus_v1_enabled": settings.FOCUS_V1_ENABLED,
        "focus_canary_percentage": settings.FOCUS_CANARY_PERCENTAGE,
        "focus_kill_switch": settings.FOCUS_KILL_SWITCH,
        "supported_misconceptions": [
            "BUG-QUAD-01",
            "BUG-QUAD-02",
            "BUG-QUAD-03",
            "BUG-QUAD-04",
            "BUG-QUAD-05",
        ],
    }
