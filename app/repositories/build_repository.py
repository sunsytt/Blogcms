from datetime import datetime, timezone

from sqlalchemy import select

from app.models.entities import Build
from app.repositories.base import BaseRepository


class BuildRepository(BaseRepository[Build]):
    model = Build

    def start(self, blog_id: int) -> Build:
        return self.add(Build(blog_id=blog_id, status="running"))

    def finish(self, build: Build, *, result: dict | None = None, error: str | None = None) -> Build:
        build.status = "failed" if error else "success"
        build.result = result
        build.error = error
        build.finished_at = datetime.now(timezone.utc)
        return self.save(build)

    def list_by_blog(self, blog_id: int, limit: int = 20) -> list[Build]:
        query = (
            select(Build)
            .where(Build.blog_id == blog_id)
            .order_by(Build.requested_at.desc(), Build.id.desc())
            .limit(limit)
        )
        return list(self.db.scalars(query))
