"""klartext.jetzt – FastAPI application entry point."""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env", override=True)

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.dependencies import get_health_checker
from api.exceptions.causal_model import CausalModelNotFoundError
from api.exceptions.narrative import (
    ActorNotFoundError,
    NarrativeFileNotFoundError,
    NarrativeNotFoundError,
    SceneNotFoundError,
)
from api.routers import claims, narratives
from api.routers.causal_models import router as causal_models_router
from api.routers.debug import router as debug_router
from api.routers.users import router as users_router
from api.services.health_service import HealthChecker, HealthStatus

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
async def handle_narrative_not_found(request: Request, exc: NarrativeNotFoundError) -> JSONResponse:
    """Translates NarrativeNotFoundError into a 404 response."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(NarrativeFileNotFoundError)
async def handle_narrative_file_not_found(
    request: Request, exc: NarrativeFileNotFoundError
) -> JSONResponse:
    """Translates NarrativeFileNotFoundError into a 404 response."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(SceneNotFoundError)
async def handle_scene_not_found(request: Request, exc: SceneNotFoundError) -> JSONResponse:
    """Translates SceneNotFoundError into a 404 response."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(ActorNotFoundError)
async def handle_actor_not_found(request: Request, exc: ActorNotFoundError) -> JSONResponse:
    """Translates ActorNotFoundError into a 404 response."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


@app.exception_handler(CausalModelNotFoundError)
async def handle_causal_model_not_found(
    request: Request, exc: CausalModelNotFoundError
) -> JSONResponse:
    """Translates CausalModelNotFoundError into a 404 response."""
    return JSONResponse(status_code=404, content={"error": str(exc)})


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(claims.router, tags=["claims"])
app.include_router(narratives.router, tags=["narratives"])
app.include_router(causal_models_router, tags=["causal-models"])
app.include_router(users_router)
app.include_router(debug_router)


@app.get("/health")
async def health(checker: HealthChecker = Depends(get_health_checker)) -> dict[str, object]:
    """Returns the health status of the API and all infrastructure dependencies.

    Always returns HTTP 200. The caller must inspect the 'status' field:
    - 'ok'       — all checks passed
    - 'degraded' — one or more checks failed (details in 'checks')
    """
    db_result = await checker.check_database()
    anthropic_result = await checker.check_anthropic()

    checks = {
        db_result.name: db_result.to_dict(),
        anthropic_result.name: anthropic_result.to_dict(),
    }
    overall = (
        HealthStatus.OK
        if all(r.status == HealthStatus.OK for r in [db_result, anthropic_result])
        else HealthStatus.DEGRADED
    )

    return {"status": overall.value, "version": "0.1.0", "checks": checks}
