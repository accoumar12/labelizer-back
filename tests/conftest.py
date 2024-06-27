import pytest
from starlette.config import environ

# Be careful where we modify the environ object, because we want to have the first instance of the config to have these environment variables
environ["DB_NAME"] = "labelizer_test"
environ["DB_SCHEMA"] = "labelizer_test"

from backend.core.database.manage import delete_all_tables, init_db
from tests.database import Session, engine
from tests.factories import test_item


@pytest.fixture(scope="session")
def db():
    delete_all_tables(engine)
    init_db(engine)
    yield
    delete_all_tables(engine)


@pytest.fixture(scope="function", autouse=True)
def session(db):
    session = Session()
    session.begin_nested()
    yield session
    session.rollback()


@pytest.fixture()
def item(session):
    return test_item
