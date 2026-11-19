from app.exceptions import NotFoundError
from app.models.entities import Project
from app.models.schemas import ProjectCreate, ProjectUpdate
from app.repositories.blog_repository import BlogRepository
from app.repositories.project_repository import ProjectRepository
from app.services._common import apply_updates


class ProjectService:
    def __init__(self, projects: ProjectRepository, blogs: BlogRepository):
        self.projects = projects
        self.blogs = blogs

    def _require_blog(self, blog_id: int) -> None:
        if self.blogs.get(blog_id) is None:
            raise NotFoundError(f"El blog {blog_id} no existe")

    def list_by_blog(self, blog_id: int) -> list[Project]:
        self._require_blog(blog_id)
        return self.projects.list_by_blog(blog_id)

    def get(self, project_id: int) -> Project:
        project = self.projects.get(project_id)
        if project is None:
            raise NotFoundError(f"El proyecto {project_id} no existe")
        return project

    def create(self, blog_id: int, data: ProjectCreate) -> Project:
        self._require_blog(blog_id)
        return self.projects.add(Project(blog_id=blog_id, **data.model_dump()))

    def update(self, project_id: int, data: ProjectUpdate) -> Project:
        project = self.get(project_id)
        apply_updates(project, data, nullable=("image_url", "repo_url"))
        return self.projects.save(project)

    def delete(self, project_id: int) -> None:
        self.projects.delete(self.get(project_id))
