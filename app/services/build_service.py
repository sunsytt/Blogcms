from app.clients.builder_client import BuilderClient
from app.exceptions import ExternalServiceError, NotFoundError
from app.models.entities import Build
from app.models.schemas import BlogRead, LandingRead, PostRead, ProjectRead
from app.repositories.blog_repository import BlogRepository
from app.repositories.build_repository import BuildRepository
from app.repositories.landing_repository import LandingRepository
from app.repositories.post_repository import PostRepository
from app.repositories.project_repository import ProjectRepository


class BuildService:
    """Coordina la generación: arma el contenido, se lo pasa al Builder y registra el resultado.

    "Subir" a Vercel NO pasa por aquí: según el diseño, lo hace la interfaz.
    """

    def __init__(
        self,
        blogs: BlogRepository,
        posts: PostRepository,
        projects: ProjectRepository,
        landings: LandingRepository,
        builds: BuildRepository,
        builder: BuilderClient,
    ):
        self.blogs = blogs
        self.posts = posts
        self.projects = projects
        self.landings = landings
        self.builds = builds
        self.builder = builder

    def _collect_content(self, blog_id: int) -> dict:
        blog = self.blogs.get(blog_id)
        if blog is None:
            raise NotFoundError(f"El blog {blog_id} no existe")
        landing = self.landings.get_by_blog(blog_id)
        return {
            "blog": BlogRead.model_validate(blog).model_dump(mode="json"),
            "posts": [
                PostRead.model_validate(p).model_dump(mode="json")
                for p in self.posts.list_by_blog(blog_id, include_drafts=True)
            ],
            "projects": [
                ProjectRead.model_validate(p).model_dump(mode="json")
                for p in self.projects.list_by_blog(blog_id)
            ],
            "landing": LandingRead.model_validate(landing).model_dump(mode="json") if landing else None,
        }

    def run(self, blog_id: int) -> Build:
        content = self._collect_content(blog_id)
        build = self.builds.start(blog_id)
        try:
            result = self.builder.build(content)
        except ExternalServiceError as exc:
            self.builds.finish(build, error=exc.message)
            raise
        return self.builds.finish(build, result=result)

    def get(self, build_id: int) -> Build:
        build = self.builds.get(build_id)
        if build is None:
            raise NotFoundError(f"La generación {build_id} no existe")
        return build

    def list_by_blog(self, blog_id: int) -> list[Build]:
        if self.blogs.get(blog_id) is None:
            raise NotFoundError(f"El blog {blog_id} no existe")
        return self.builds.list_by_blog(blog_id)
