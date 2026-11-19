"""Capa CONTROLLERS: reciben la petición HTTP, delegan al service y devuelven la respuesta."""
from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_blog_service
from app.models.schemas import BlogCreate, BlogRead, BlogUpdate
from app.services.blog_service import BlogService

router = APIRouter(prefix="/api/blogs", tags=["Blogs"])


@router.get("", response_model=list[BlogRead])
def list_blogs(service: BlogService = Depends(get_blog_service)):
    return service.list()


@router.post("", response_model=BlogRead, status_code=status.HTTP_201_CREATED)
def create_blog(data: BlogCreate, service: BlogService = Depends(get_blog_service)):
    return service.create(data)


@router.get("/{blog_id}", response_model=BlogRead)
def get_blog(blog_id: int, service: BlogService = Depends(get_blog_service)):
    return service.get(blog_id)


@router.put("/{blog_id}", response_model=BlogRead)
def update_blog(blog_id: int, data: BlogUpdate, service: BlogService = Depends(get_blog_service)):
    return service.update(blog_id, data)


@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(blog_id: int, service: BlogService = Depends(get_blog_service)):
    service.delete(blog_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
