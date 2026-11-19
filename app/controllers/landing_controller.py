from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_landing_service
from app.models.schemas import LandingRead, LandingUpsert
from app.services.landing_service import LandingService

router = APIRouter(prefix="/api/blogs/{blog_id}/landing", tags=["Landing"])


@router.get("", response_model=LandingRead)
def get_landing(blog_id: int, service: LandingService = Depends(get_landing_service)):
    return service.get(blog_id)


@router.put("", response_model=LandingRead)
def upsert_landing(
    blog_id: int, data: LandingUpsert, service: LandingService = Depends(get_landing_service)
):
    """Crea la landing del blog o la reemplaza completa."""
    return service.upsert(blog_id, data)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_landing(blog_id: int, service: LandingService = Depends(get_landing_service)):
    service.delete(blog_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
