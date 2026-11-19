from sqlalchemy import select

from app.models.entities import Blog
from app.repositories.base import BaseRepository


class BlogRepository(BaseRepository[Blog]):
    model = Blog

    def list_all(self) -> list[Blog]:
        return list(self.db.scalars(select(Blog).order_by(Blog.id)))

    def get_by_slug(self, slug: str) -> Blog | None:
        return self.db.scalar(select(Blog).where(Blog.slug == slug))
