from app.clients.metrics_client import MetricsClient
from app.exceptions import NotFoundError
from app.models.schemas import MetricsRead
from app.repositories.blog_repository import BlogRepository


class MetricsService:
    def __init__(self, blogs: BlogRepository, metrics: MetricsClient):
        self.blogs = blogs
        self.metrics = metrics

    def get(self, blog_id: int) -> MetricsRead:
        if self.blogs.get(blog_id) is None:
            raise NotFoundError(f"El blog {blog_id} no existe")
        data = self.metrics.get_metrics(blog_id)
        return MetricsRead(blog_id=blog_id, visitas=data["visitas"], visitantesUnicos=data["visitantesUnicos"])
