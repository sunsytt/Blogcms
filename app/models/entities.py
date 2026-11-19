"""Capa MODELS (parte 1): tablas de la base de datos con SQLAlchemy."""
from datetime import date, datetime

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

# En PostgreSQL es un arreglo nativo (TEXT[]). El variant JSON solo existe para
# poder correr las pruebas automáticas con SQLite sin cambiar el código.
StringList = ARRAY(String).with_variant(JSON(), "sqlite")


class Blog(Base):
    __tablename__ = "blogs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    slug: Mapped[str] = mapped_column(String(120), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    site_url: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    posts: Mapped[list["Post"]] = relationship(
        back_populates="blog", cascade="all, delete-orphan", order_by="Post.pub_date.desc()"
    )
    projects: Mapped[list["Project"]] = relationship(
        back_populates="blog", cascade="all, delete-orphan", order_by="Project.position"
    )
    landing: Mapped["Landing | None"] = relationship(
        back_populates="blog", cascade="all, delete-orphan", uselist=False
    )
    builds: Mapped[list["Build"]] = relationship(
        back_populates="blog", cascade="all, delete-orphan", order_by="Build.requested_at.desc()"
    )


class Post(Base):
    """Un artículo. Los campos replican el schema de Zod del blog en Astro."""

    __tablename__ = "posts"
    __table_args__ = (UniqueConstraint("blog_id", "slug", name="uq_posts_blog_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    slug: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(String(160))  # el blog falla el build si pasa de 160
    body_markdown: Mapped[str] = mapped_column(Text, default="")
    hero_image_url: Mapped[str | None] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(80))
    tags: Mapped[list[str]] = mapped_column(StringList, default=list)
    pub_date: Mapped[date] = mapped_column(Date)
    updated_date: Mapped[date | None] = mapped_column(Date)
    draft: Mapped[bool] = mapped_column(Boolean, default=False)

    blog: Mapped[Blog] = relationship(back_populates="posts")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500))
    technologies: Mapped[list[str]] = mapped_column(StringList, default=list)
    role: Mapped[str] = mapped_column(Text, default="")
    learnings: Mapped[str] = mapped_column(Text, default="")
    repo_url: Mapped[str | None] = mapped_column(String(500))
    featured: Mapped[bool] = mapped_column(Boolean, default=False)
    position: Mapped[int] = mapped_column(Integer, default=0)

    blog: Mapped[Blog] = relationship(back_populates="projects")


class Landing(Base):
    __tablename__ = "landings"

    id: Mapped[int] = mapped_column(primary_key=True)
    blog_id: Mapped[int] = mapped_column(
        ForeignKey("blogs.id", ondelete="CASCADE"), unique=True, index=True
    )
    site_title: Mapped[str] = mapped_column(String(200))
    meta_description: Mapped[str] = mapped_column(String(300), default="")
    hero_title: Mapped[str] = mapped_column(String(300))
    hero_text: Mapped[str] = mapped_column(Text, default="")
    hero_primary_label: Mapped[str] = mapped_column(String(80), default="")
    hero_secondary_label: Mapped[str] = mapped_column(String(80), default="")
    about_title: Mapped[str] = mapped_column(String(120), default="Sobre mí")
    about_paragraphs: Mapped[list[str]] = mapped_column(StringList, default=list)
    contact_title: Mapped[str] = mapped_column(String(120), default="Contacto")
    contact_text: Mapped[str] = mapped_column(Text, default="")
    footer_text: Mapped[str] = mapped_column(String(300), default="")

    blog: Mapped[Blog] = relationship(back_populates="landing")
    tech_groups: Mapped[list["LandingTechGroup"]] = relationship(
        back_populates="landing", cascade="all, delete-orphan", order_by="LandingTechGroup.position"
    )
    timeline_entries: Mapped[list["LandingTimelineEntry"]] = relationship(
        back_populates="landing",
        cascade="all, delete-orphan",
        order_by="LandingTimelineEntry.position",
    )
    links: Mapped[list["LandingLink"]] = relationship(
        back_populates="landing", cascade="all, delete-orphan", order_by="LandingLink.position"
    )


class LandingTechGroup(Base):
    """Grupo de chips (Web, Android...). is_learning_now marca el bloque 'Aprendiendo ahora'."""

    __tablename__ = "landing_tech_groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    landing_id: Mapped[int] = mapped_column(ForeignKey("landings.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    position: Mapped[int] = mapped_column(Integer, default=0)
    is_learning_now: Mapped[bool] = mapped_column(Boolean, default=False)

    landing: Mapped[Landing] = relationship(back_populates="tech_groups")
    items: Mapped[list["LandingTechItem"]] = relationship(
        back_populates="group", cascade="all, delete-orphan", order_by="LandingTechItem.position"
    )


class LandingTechItem(Base):
    __tablename__ = "landing_tech_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("landing_tech_groups.id", ondelete="CASCADE"), index=True
    )
    label: Mapped[str] = mapped_column(String(120))
    position: Mapped[int] = mapped_column(Integer, default=0)

    group: Mapped[LandingTechGroup] = relationship(back_populates="items")


class LandingTimelineEntry(Base):
    __tablename__ = "landing_timeline_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    landing_id: Mapped[int] = mapped_column(ForeignKey("landings.id", ondelete="CASCADE"), index=True)
    date_label: Mapped[str] = mapped_column(String(40))  # texto libre: "2025–2026"
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    position: Mapped[int] = mapped_column(Integer, default=0)

    landing: Mapped[Landing] = relationship(back_populates="timeline_entries")


class LandingLink(Base):
    __tablename__ = "landing_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    landing_id: Mapped[int] = mapped_column(ForeignKey("landings.id", ondelete="CASCADE"), index=True)
    label: Mapped[str] = mapped_column(String(80))
    url: Mapped[str] = mapped_column(String(500))
    detail: Mapped[str | None] = mapped_column(String(200))  # texto secundario, ej. "github.com/usuario"
    position: Mapped[int] = mapped_column(Integer, default=0)

    landing: Mapped[Landing] = relationship(back_populates="links")


class Build(Base):
    """Registro de cada generación del sitio pedida al Builder."""

    __tablename__ = "builds"

    id: Mapped[int] = mapped_column(primary_key=True)
    blog_id: Mapped[int] = mapped_column(ForeignKey("blogs.id", ondelete="CASCADE"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="running")  # running | success | failed
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    result: Mapped[dict | None] = mapped_column(JSON)
    error: Mapped[str | None] = mapped_column(Text)

    blog: Mapped[Blog] = relationship(back_populates="builds")
