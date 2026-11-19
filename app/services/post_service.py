from sqlalchemy.exc import IntegrityError

from app.exceptions import ConflictError, NotFoundError
from app.models.entities import Post
from app.models.schemas import PostCreate, PostUpdate
from app.repositories.blog_repository import BlogRepository
from app.repositories.post_repository import PostRepository
from app.services._common import apply_updates

_SLUG_TAKEN = "Ya existe un artículo con ese slug en este blog"


class PostService:
    def __init__(self, posts: PostRepository, blogs: BlogRepository):
        self.posts = posts
        self.blogs = blogs

    def _require_blog(self, blog_id: int) -> None:
        if self.blogs.get(blog_id) is None:
            raise NotFoundError(f"El blog {blog_id} no existe")

    def list_by_blog(self, blog_id: int, include_drafts: bool = True) -> list[Post]:
        self._require_blog(blog_id)
        return self.posts.list_by_blog(blog_id, include_drafts)

    def get(self, post_id: int) -> Post:
        post = self.posts.get(post_id)
        if post is None:
            raise NotFoundError(f"El artículo {post_id} no existe")
        return post

    def create(self, blog_id: int, data: PostCreate) -> Post:
        self._require_blog(blog_id)
        try:
            return self.posts.add(Post(blog_id=blog_id, **data.model_dump()))
        except IntegrityError as exc:
            raise ConflictError(_SLUG_TAKEN) from exc

    def update(self, post_id: int, data: PostUpdate) -> Post:
        post = self.get(post_id)
        apply_updates(post, data, nullable=("hero_image_url", "updated_date"))
        try:
            return self.posts.save(post)
        except IntegrityError as exc:
            raise ConflictError(_SLUG_TAKEN) from exc

    def delete(self, post_id: int) -> None:
        self.posts.delete(self.get(post_id))
