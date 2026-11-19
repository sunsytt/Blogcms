from sqlalchemy import select

from app.models.entities import (
    Landing,
    LandingLink,
    LandingTechGroup,
    LandingTechItem,
    LandingTimelineEntry,
)
from app.models.schemas import LandingUpsert
from app.repositories.base import BaseRepository

_SCALAR_FIELDS = (
    "site_title",
    "meta_description",
    "hero_title",
    "hero_text",
    "hero_primary_label",
    "hero_secondary_label",
    "about_title",
    "about_paragraphs",
    "contact_title",
    "contact_text",
    "footer_text",
)


class LandingRepository(BaseRepository[Landing]):
    model = Landing

    def get_by_blog(self, blog_id: int) -> Landing | None:
        return self.db.scalar(select(Landing).where(Landing.blog_id == blog_id))

    def upsert(self, blog_id: int, data: LandingUpsert) -> Landing:
        """Crea la landing del blog o la reemplaza completa (campos y listas)."""
        landing = self.get_by_blog(blog_id)
        if landing is None:
            landing = Landing(blog_id=blog_id)
            self.db.add(landing)

        for field in _SCALAR_FIELDS:
            setattr(landing, field, getattr(data, field))

        # Se reemplazan las listas; delete-orphan borra las filas anteriores.
        landing.tech_groups = [
            LandingTechGroup(
                name=group.name,
                is_learning_now=group.is_learning_now,
                position=g_pos,
                items=[
                    LandingTechItem(label=label, position=i_pos)
                    for i_pos, label in enumerate(group.items)
                ],
            )
            for g_pos, group in enumerate(data.tech_groups)
        ]
        landing.timeline_entries = [
            LandingTimelineEntry(
                date_label=entry.date_label,
                title=entry.title,
                description=entry.description,
                position=pos,
            )
            for pos, entry in enumerate(data.timeline_entries)
        ]
        landing.links = [
            LandingLink(label=link.label, url=link.url, detail=link.detail, position=pos)
            for pos, link in enumerate(data.links)
        ]
        return self.save(landing)
