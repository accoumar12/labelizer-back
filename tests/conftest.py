import pytest
from starlette.config import environ

# Be careful where we modify the environ object, because we want to have the first instance of the config to have these environment variables
environ["DB_NAME"] = "labelizer_test"
environ["DB_SCHEMA"] = "labelizer_test"

from backend.core.database.manage import create_all_tables, drop_all_tables
from tests.database import Session, engine
from tests.test_data import test_item, test_triplet, test_validation_triplet


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


@pytest.fixture()
def triplet(session):
    session.add(test_triplet)
    session.commit()
    return test_triplet


@pytest.fixture()
def validation_triplet(session):
    session.add(test_validation_triplet)
    session.commit()
    return test_validation_triplet
