"""Arma cada service con sus repositories y clients (inyección de dependencias de FastAPI)."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.builder_client import BuilderClient, get_builder_client
from app.clients.metrics_client import MetricsClient, get_metrics_client
from app.config import Settings, get_settings
from app.database import get_db
from app.repositories.blog_repository import BlogRepository
from app.repositories.build_repository import BuildRepository
from app.repositories.landing_repository import LandingRepository
from app.repositories.post_repository import PostRepository
from app.repositories.project_repository import ProjectRepository
from app.services.blog_service import BlogService
from app.services.build_service import BuildService
from app.services.landing_service import LandingService
from app.services.metrics_service import MetricsService
from app.services.post_service import PostService
from app.services.project_service import ProjectService


def get_builder(settings: Settings = Depends(get_settings)) -> BuilderClient:
    return get_builder_client(settings)


def get_metrics(settings: Settings = Depends(get_settings)) -> MetricsClient:
    return get_metrics_client(settings)


def get_blog_service(db: Session = Depends(get_db)) -> BlogService:
    return BlogService(BlogRepository(db))


def get_post_service(db: Session = Depends(get_db)) -> PostService:
    return PostService(PostRepository(db), BlogRepository(db))


def get_project_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(ProjectRepository(db), BlogRepository(db))


def get_landing_service(db: Session = Depends(get_db)) -> LandingService:
    return LandingService(LandingRepository(db), BlogRepository(db))


def get_build_service(
    db: Session = Depends(get_db), builder: BuilderClient = Depends(get_builder)
) -> BuildService:
    return BuildService(
        BlogRepository(db),
        PostRepository(db),
        ProjectRepository(db),
        LandingRepository(db),
        BuildRepository(db),
        builder,
    )


def get_metrics_service(
    db: Session = Depends(get_db), metrics: MetricsClient = Depends(get_metrics)
) -> MetricsService:
    return MetricsService(BlogRepository(db), metrics)
