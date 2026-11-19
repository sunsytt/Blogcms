import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.clients.builder_client import BuilderClient
from app.database import Base, get_db
from app.dependencies import get_builder
from app.exceptions import ExternalServiceError
from app.main import app


@pytest.fixture()
def client():
    # SQLite en memoria solo para pruebas; la API real usa PostgreSQL.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class FailingBuilder:
    def build(self, payload: dict) -> dict:
        raise ExternalServiceError("Builder caído")


@pytest.fixture()
def failing_builder() -> BuilderClient:
    app.dependency_overrides[get_builder] = lambda: FailingBuilder()
    yield
    app.dependency_overrides.pop(get_builder, None)
