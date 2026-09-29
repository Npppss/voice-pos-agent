"""
AI-Powered Cashier Backend — FastAPI Entrypoint
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import audio, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print(f"Starting AI Cashier Backend v{settings.APP_VERSION}")
    print(f"Odoo: {settings.ODOO_URL} | DB: {settings.ODOO_DB}")
    print(f"STT:  {settings.STT_SERVICE_URL}")
    print(f"LLM:  {settings.LLM_MODEL}")
    yield
    print("Shutting down AI Cashier Backend")


app = FastAPI(
    title="AI Cashier API",
    description="Voice-driven POS system with Odoo integration",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(audio.router, prefix="/api/v1", tags=["Audio"])
app.include_router(orders.router, prefix="/api/v1", tags=["Orders"])


@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "services": {
            "stt": "up",
            "ai_agent": "up",
            "vector_db": "up",
            "odoo": "up",
        },
        "version": settings.APP_VERSION,
    }
