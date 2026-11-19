from fastapi import APIRouter, Depends

from app.dependencies import get_build_service
from app.models.schemas import BuildRead, BuildRequest
from app.services.build_service import BuildService

router = APIRouter(tags=["Generación"])


@router.post("/api/build", response_model=BuildRead)
def build_site(request: BuildRequest, service: BuildService = Depends(get_build_service)):
    """Pide al Builder que genere el sitio del blog. Publicar en Vercel es un paso aparte."""
    return service.run(request.blog_id)


@router.get("/api/build/{build_id}", response_model=BuildRead)
def get_build(build_id: int, service: BuildService = Depends(get_build_service)):
    return service.get(build_id)


@router.get("/api/blogs/{blog_id}/builds", response_model=list[BuildRead])
def list_builds(blog_id: int, service: BuildService = Depends(get_build_service)):
    return service.list_by_blog(blog_id)
