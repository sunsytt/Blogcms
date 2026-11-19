from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.controllers import (
    blog_controller,
    build_controller,
    landing_controller,
    metrics_controller,
    post_controller,
    project_controller,
)
from app.exceptions import ConflictError, ExternalServiceError, NotFoundError

app = FastAPI(title="API del CMS", version="0.1.0")

# La interfaz (alojada en Vercel) es la única que consume esta API. Restringe los
# orígenes a su dominio real antes de desplegar.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (
    blog_controller,
    post_controller,
    project_controller,
    landing_controller,
    build_controller,
    metrics_controller,
):
    app.include_router(module.router)


@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(ConflictError)
async def conflict_handler(_: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.message})


@app.exception_handler(ExternalServiceError)
async def external_handler(_: Request, exc: ExternalServiceError):
    return JSONResponse(status_code=502, content={"detail": exc.message})


@app.get("/health", tags=["Sistema"])
def health():
    return {"status": "ok"}
