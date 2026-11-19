"""esquema inicial del CMS

Revision ID: 0001
Revises:
Create Date: 2026-11-08
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "blogs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(120), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("site_url", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "posts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("blog_id", sa.Integer(), sa.ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.String(160), nullable=False),
        sa.Column("body_markdown", sa.Text(), nullable=False),
        sa.Column("hero_image_url", sa.String(500)),
        sa.Column("category", sa.String(80), nullable=False),
        sa.Column("tags", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("pub_date", sa.Date(), nullable=False),
        sa.Column("updated_date", sa.Date()),
        sa.Column("draft", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("blog_id", "slug", name="uq_posts_blog_slug"),
    )
    op.create_index("ix_posts_blog_id", "posts", ["blog_id"])

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("blog_id", sa.Integer(), sa.ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(500)),
        sa.Column("technologies", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),
        sa.Column("learnings", sa.Text(), nullable=False),
        sa.Column("repo_url", sa.String(500)),
        sa.Column("featured", sa.Boolean(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_index("ix_projects_blog_id", "projects", ["blog_id"])

    op.create_table(
        "landings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "blog_id", sa.Integer(), sa.ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False, unique=True
        ),
        sa.Column("site_title", sa.String(200), nullable=False),
        sa.Column("meta_description", sa.String(300), nullable=False),
        sa.Column("hero_title", sa.String(300), nullable=False),
        sa.Column("hero_text", sa.Text(), nullable=False),
        sa.Column("hero_primary_label", sa.String(80), nullable=False),
        sa.Column("hero_secondary_label", sa.String(80), nullable=False),
        sa.Column("about_title", sa.String(120), nullable=False),
        sa.Column("about_paragraphs", postgresql.ARRAY(sa.String()), nullable=False),
        sa.Column("contact_title", sa.String(120), nullable=False),
        sa.Column("contact_text", sa.Text(), nullable=False),
        sa.Column("footer_text", sa.String(300), nullable=False),
    )
    op.create_index("ix_landings_blog_id", "landings", ["blog_id"])

    op.create_table(
        "landing_tech_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "landing_id", sa.Integer(), sa.ForeignKey("landings.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("is_learning_now", sa.Boolean(), nullable=False),
    )
    op.create_index("ix_landing_tech_groups_landing_id", "landing_tech_groups", ["landing_id"])

    op.create_table(
        "landing_tech_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "group_id", sa.Integer(), sa.ForeignKey("landing_tech_groups.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("label", sa.String(120), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_index("ix_landing_tech_items_group_id", "landing_tech_items", ["group_id"])

    op.create_table(
        "landing_timeline_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "landing_id", sa.Integer(), sa.ForeignKey("landings.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("date_label", sa.String(40), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_index("ix_landing_timeline_entries_landing_id", "landing_timeline_entries", ["landing_id"])

    op.create_table(
        "landing_links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "landing_id", sa.Integer(), sa.ForeignKey("landings.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("label", sa.String(80), nullable=False),
        sa.Column("url", sa.String(500), nullable=False),
        sa.Column("detail", sa.String(200)),
        sa.Column("position", sa.Integer(), nullable=False),
    )
    op.create_index("ix_landing_links_landing_id", "landing_links", ["landing_id"])

    op.create_table(
        "builds",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("blog_id", sa.Integer(), sa.ForeignKey("blogs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("requested_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True)),
        sa.Column("result", sa.JSON()),
        sa.Column("error", sa.Text()),
    )
    op.create_index("ix_builds_blog_id", "builds", ["blog_id"])


def downgrade() -> None:
    for table in (
        "builds",
        "landing_links",
        "landing_timeline_entries",
        "landing_tech_items",
        "landing_tech_groups",
        "landings",
        "projects",
        "posts",
        "blogs",
    ):
        op.drop_table(table)
