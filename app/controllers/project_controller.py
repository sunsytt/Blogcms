from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_project_service
from app.models.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter(tags=["Proyectos"])


@router.get("/api/blogs/{blog_id}/projects", response_model=list[ProjectRead])
def list_projects(blog_id: int, service: ProjectService = Depends(get_project_service)):
    return service.list_by_blog(blog_id)


@router.post(
    "/api/blogs/{blog_id}/projects", response_model=ProjectRead, status_code=status.HTTP_201_CREATED
)
def create_project(
    blog_id: int, data: ProjectCreate, service: ProjectService = Depends(get_project_service)
):
    return service.create(blog_id, data)


@router.get("/api/projects/{project_id}", response_model=ProjectRead)
def get_project(project_id: int, service: ProjectService = Depends(get_project_service)):
    return service.get(project_id)


@router.put("/api/projects/{project_id}", response_model=ProjectRead)
def update_project(
    project_id: int, data: ProjectUpdate, service: ProjectService = Depends(get_project_service)
):
    return service.update(project_id, data)


@router.delete("/api/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, service: ProjectService = Depends(get_project_service)):
    service.delete(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
