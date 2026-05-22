"""klartext.jetzt – FastAPI application entry point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.exceptions.narrative import (
    NarrativeFileNotFoundError,
    NarrativeNotFoundError,
    SceneNotFoundError,
)
from api.routers import claims, narratives

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


# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------


@app.exception_handler(NarrativeNotFoundError)
async def handle_narrative_not_found(
    request: Request, exc: NarrativeNotFoundError
) -> JSONResponse:
    """Translates NarrativeNotFoundError into a 404 response."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(NarrativeFileNotFoundError)
async def handle_narrative_file_not_found(
    request: Request, exc: NarrativeFileNotFoundError
) -> JSONResponse:
    """Translates NarrativeFileNotFoundError into a 404 response."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(SceneNotFoundError)
async def handle_scene_not_found(
    request: Request, exc: SceneNotFoundError
) -> JSONResponse:
    """Translates SceneNotFoundError into a 404 response."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(claims.router, tags=["claims"])
app.include_router(narratives.router, tags=["narratives"])


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}
