from sqlalchemy import select

from app.models.entities import Project
from app.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    model = Project

    def list_by_blog(self, blog_id: int) -> list[Project]:
        query = select(Project).where(Project.blog_id == blog_id).order_by(Project.position, Project.id)
        return list(self.db.scalars(query))
