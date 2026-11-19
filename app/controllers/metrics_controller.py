from fastapi import APIRouter, Depends

from app.dependencies import get_metrics_service
from app.models.schemas import MetricsRead
from app.services.metrics_service import MetricsService

router = APIRouter(tags=["Métricas"])


@router.get("/api/metrics/{blog_id}", response_model=MetricsRead)
def get_metrics(blog_id: int, service: MetricsService = Depends(get_metrics_service)):
    return service.get(blog_id)
