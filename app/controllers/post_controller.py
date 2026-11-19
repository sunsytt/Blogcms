from fastapi import APIRouter, Depends, Response, status

from app.dependencies import get_post_service
from app.models.schemas import PostCreate, PostRead, PostUpdate
from app.services.post_service import PostService

router = APIRouter(tags=["Artículos"])


@router.get("/api/blogs/{blog_id}/posts", response_model=list[PostRead])
def list_posts(
    blog_id: int, include_drafts: bool = True, service: PostService = Depends(get_post_service)
):
    return service.list_by_blog(blog_id, include_drafts)


@router.post(
    "/api/blogs/{blog_id}/posts", response_model=PostRead, status_code=status.HTTP_201_CREATED
)
def create_post(blog_id: int, data: PostCreate, service: PostService = Depends(get_post_service)):
    return service.create(blog_id, data)


@router.get("/api/posts/{post_id}", response_model=PostRead)
def get_post(post_id: int, service: PostService = Depends(get_post_service)):
    return service.get(post_id)


@router.put("/api/posts/{post_id}", response_model=PostRead)
def update_post(post_id: int, data: PostUpdate, service: PostService = Depends(get_post_service)):
    return service.update(post_id, data)


@router.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, service: PostService = Depends(get_post_service)):
    service.delete(post_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
