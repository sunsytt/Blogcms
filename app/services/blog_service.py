"""Capa SERVICES: reglas de negocio. No conocen HTTP ni SQL directo."""
from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictError, NotFoundError
from app.models.entities import Blog
from app.models.schemas import BlogCreate, BlogUpdate
from app.repositories.blog_repository import BlogRepository
from app.services._common import apply_updates

_SLUG_TAKEN = "Ya existe un blog con ese slug"


class BlogService:
    def __init__(self, blogs: BlogRepository):
        self.blogs = blogs

    def list(self) -> list[Blog]:
        return self.blogs.list_all()

    def get(self, blog_id: int) -> Blog:
        blog = self.blogs.get(blog_id)
        if blog is None:
            raise NotFoundError(f"El blog {blog_id} no existe")
        return blog

    def create(self, data: BlogCreate) -> Blog:
        if self.blogs.get_by_slug(data.slug):
            raise ConflictError(_SLUG_TAKEN)
        try:
            return self.blogs.add(Blog(**data.model_dump()))
        except IntegrityError as exc:
            raise ConflictError(_SLUG_TAKEN) from exc

    def update(self, blog_id: int, data: BlogUpdate) -> Blog:
        blog = self.get(blog_id)
        apply_updates(blog, data, nullable=("site_url",))
        try:
            return self.blogs.save(blog)
        except IntegrityError as exc:
            raise ConflictError(_SLUG_TAKEN) from exc

    def delete(self, blog_id: int) -> None:
        self.blogs.delete(self.get(blog_id))
