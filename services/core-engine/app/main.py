from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as session_router

app = FastAPI(
    title="Kişisel Öğrenme Motoru - CAS & Bilişsel Çekirdek Servisi",
    version="1.0.0",
    description="Nöro-Sembolik Adaptif Öğrenme Sistemi Çekirdek API",
)

# CORS ayarları (Next.js istemcisi için)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session_router)


@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "core-engine",
        "cas_status": "ready",
        "supported_misconceptions": [
            "BUG-QUAD-01",
            "BUG-QUAD-02",
            "BUG-QUAD-03",
            "BUG-QUAD-04",
            "BUG-QUAD-05",
        ],
    }
