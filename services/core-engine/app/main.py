from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.endpoints import router as session_router

# Yapılandırılmış JSON Loglama Kurulumu
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    title="Kişisel Öğrenme Motoru - CAS & Bilişsel Çekirdek Servisi",
    version="1.0.0",
    description="Nöro-Sembolik Adaptif Öğrenme Sistemi Çekirdek API",
    debug=settings.DEBUG,
)

# Sıkılaştırılmış CORS ayarları (app/core/config.py ve .env kaynaklı)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(session_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "core-engine",
        "environment": settings.ENVIRONMENT,
        "cas_status": "ready",
        "supported_misconceptions": [
            "BUG-QUAD-01",
            "BUG-QUAD-02",
            "BUG-QUAD-03",
            "BUG-QUAD-04",
            "BUG-QUAD-05",
        ],
    }
