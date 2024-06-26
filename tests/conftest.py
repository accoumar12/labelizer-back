from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from backend.core.api.fast_api_app import app
from backend.core.database.core import engine
from sqlalchemy.orm import Session


@pytest.fixture(dataset="session", autouse=True)
def db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


@pytest.fixture(dataset="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client
