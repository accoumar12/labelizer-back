import pytest
from starlette.config import environ

# Be careful where we modify the environ object, because we want to have the first instance of the config to have these environment variables
environ["DB_NAME"] = "labelizer_test"
environ["DB_SCHEMA"] = "labelizer_test"

from backend.core.database.manage import create_all_tables, drop_all_tables
from tests.database import Session, engine
from tests.factories import test_item


@pytest.fixture(scope="session")
def db():
    drop_all_tables(engine)
    create_all_tables(engine)
    yield
    drop_all_tables(engine)


@pytest.fixture(scope="function", autouse=True)
def session(db):
    session = Session()
    session.begin_nested()
    yield session
    session.rollback()


@pytest.fixture()
def item(session):
    session.add(test_item)
    session.commit()
    return test_item
