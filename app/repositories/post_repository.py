from sqlalchemy import select

from app.models.entities import Post
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    model = Post

    def list_by_blog(self, blog_id: int, include_drafts: bool = True) -> list[Post]:
        query = select(Post).where(Post.blog_id == blog_id)
        if not include_drafts:
            query = query.where(Post.draft.is_(False))
        return list(self.db.scalars(query.order_by(Post.pub_date.desc(), Post.id.desc())))
