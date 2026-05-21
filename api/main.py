"""klartext.jetzt – FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import claims

app = FastAPI(
    title="klartext.jetzt API",
    description="KI-Serviceschicht für Claim-Extraktion und Konsistenzprüfung",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(claims.router, tags=["claims"])


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "version": "0.1.0"}
