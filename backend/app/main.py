from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.api_router import api_router


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description=(
        "API para la plataforma "
        "de reservas de barberías."
    )
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(
    api_router,
    prefix="/api/v1"
)


@app.get("/")
def root():
    return {
        "application": settings.APP_NAME,
        "status": "online",
        "api_version": "v1",
        "docs": "/docs"
    }