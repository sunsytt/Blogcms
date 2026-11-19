"""Capa MODELS (parte 2): esquemas Pydantic de entrada y salida de la API."""
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

SLUG_PATTERN = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --------------------------------------------------------------------- Blogs
class BlogBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(pattern=SLUG_PATTERN, max_length=120)
    description: str = ""
    site_url: str | None = Field(default=None, max_length=255)


class BlogCreate(BlogBase):
    pass


class BlogUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, pattern=SLUG_PATTERN, max_length=120)
    description: str | None = None
    site_url: str | None = Field(default=None, max_length=255)


class BlogRead(BlogBase, ORMModel):
    id: int
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------- Posts
class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    slug: str = Field(pattern=SLUG_PATTERN, max_length=200)
    # Mismo límite que el schema de Zod del blog: si se pasa, astro build falla.
    description: str = Field(max_length=160)
    body_markdown: str = ""
    hero_image_url: str | None = Field(default=None, max_length=500)
    category: str = Field(min_length=1, max_length=80)
    tags: list[str] = Field(default_factory=list)
    pub_date: date
    updated_date: date | None = None
    draft: bool = False


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    slug: str | None = Field(default=None, pattern=SLUG_PATTERN, max_length=200)
    description: str | None = Field(default=None, max_length=160)
    body_markdown: str | None = None
    hero_image_url: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    tags: list[str] | None = None
    pub_date: date | None = None
    updated_date: date | None = None
    draft: bool | None = None


class PostRead(PostBase, ORMModel):
    id: int
    blog_id: int


# ------------------------------------------------------------------ Projects
class ProjectBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str
    image_url: str | None = Field(default=None, max_length=500)
    technologies: list[str] = Field(default_factory=list)
    role: str = ""
    learnings: str = ""
    repo_url: str | None = Field(default=None, max_length=500)
    featured: bool = False
    position: int = 0


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    image_url: str | None = Field(default=None, max_length=500)
    technologies: list[str] | None = None
    role: str | None = None
    learnings: str | None = None
    repo_url: str | None = Field(default=None, max_length=500)
    featured: bool | None = None
    position: int | None = None


class ProjectRead(ProjectBase, ORMModel):
    id: int
    blog_id: int


# ------------------------------------------------------------------- Landing
class TechGroupIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    is_learning_now: bool = False
    items: list[str] = Field(default_factory=list)  # el orden de la lista define la posición


class TimelineEntryIn(BaseModel):
    date_label: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=200)
    description: str = ""


class LinkIn(BaseModel):
    label: str = Field(min_length=1, max_length=80)
    url: str = Field(min_length=1, max_length=500)
    detail: str | None = Field(default=None, max_length=200)


class LandingUpsert(BaseModel):
    """Se envía la landing completa; el CMS reemplaza sus listas internas."""

    site_title: str = Field(min_length=1, max_length=200)
    meta_description: str = Field(default="", max_length=300)
    hero_title: str = Field(min_length=1, max_length=300)
    hero_text: str = ""
    hero_primary_label: str = Field(default="", max_length=80)
    hero_secondary_label: str = Field(default="", max_length=80)
    about_title: str = Field(default="Sobre mí", max_length=120)
    about_paragraphs: list[str] = Field(default_factory=list)
    contact_title: str = Field(default="Contacto", max_length=120)
    contact_text: str = ""
    footer_text: str = Field(default="", max_length=300)
    tech_groups: list[TechGroupIn] = Field(default_factory=list)
    timeline_entries: list[TimelineEntryIn] = Field(default_factory=list)
    links: list[LinkIn] = Field(default_factory=list)


class TechGroupRead(ORMModel):
    name: str
    is_learning_now: bool
    items: list[str]

    @field_validator("items", mode="before")
    @classmethod
    def _items_to_labels(cls, value: Any) -> Any:
        return [item if isinstance(item, str) else item.label for item in value]


class TimelineEntryRead(TimelineEntryIn, ORMModel):
    pass


class LinkRead(LinkIn, ORMModel):
    pass


class LandingRead(ORMModel):
    id: int
    blog_id: int
    site_title: str
    meta_description: str
    hero_title: str
    hero_text: str
    hero_primary_label: str
    hero_secondary_label: str
    about_title: str
    about_paragraphs: list[str]
    contact_title: str
    contact_text: str
    footer_text: str
    tech_groups: list[TechGroupRead]
    timeline_entries: list[TimelineEntryRead]
    links: list[LinkRead]


# -------------------------------------------------------------------- Builds
class BuildRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    blog_id: int = Field(alias="blogId")


class BuildRead(ORMModel):
    id: int
    blog_id: int = Field(serialization_alias="blogId")
    status: str
    requested_at: datetime
    finished_at: datetime | None = None
    result: dict | None = None
    error: str | None = None


# ------------------------------------------------------------------ Métricas
class MetricsRead(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    blog_id: int = Field(serialization_alias="blogId")
    visitas: int
    visitantes_unicos: int = Field(alias="visitantesUnicos", serialization_alias="visitantesUnicos")
