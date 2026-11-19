from app.exceptions import NotFoundError
from app.models.entities import Landing
from app.models.schemas import LandingUpsert
from app.repositories.blog_repository import BlogRepository
from app.repositories.landing_repository import LandingRepository


class LandingService:
    def __init__(self, landings: LandingRepository, blogs: BlogRepository):
        self.landings = landings
        self.blogs = blogs

    def _require_blog(self, blog_id: int) -> None:
        if self.blogs.get(blog_id) is None:
            raise NotFoundError(f"El blog {blog_id} no existe")

    def get(self, blog_id: int) -> Landing:
        self._require_blog(blog_id)
        landing = self.landings.get_by_blog(blog_id)
        if landing is None:
            raise NotFoundError(f"El blog {blog_id} aún no tiene landing")
        return landing

    def upsert(self, blog_id: int, data: LandingUpsert) -> Landing:
        self._require_blog(blog_id)
        return self.landings.upsert(blog_id, data)

    def delete(self, blog_id: int) -> None:
        self.landings.delete(self.get(blog_id))
