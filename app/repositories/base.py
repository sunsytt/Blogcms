"""Capa REPOSITORY: único lugar donde se habla con la base de datos."""
from typing import Generic, TypeVar

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: type[T]

    def __init__(self, db: Session):
        self.db = db

    def get(self, entity_id: int) -> T | None:
        return self.db.get(self.model, entity_id)

    def add(self, entity: T) -> T:
        self.db.add(entity)
        return self._commit(entity)

    def save(self, entity: T) -> T:
        return self._commit(entity)

    def delete(self, entity: T) -> None:
        self.db.delete(entity)
        self._commit()

    def _commit(self, entity: T | None = None) -> T | None:
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise  # el service lo traduce a un error de negocio (409)
        if entity is not None:
            self.db.refresh(entity)
        return entity
