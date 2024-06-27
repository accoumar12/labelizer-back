import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from starlette.config import environ

from backend.core.database.manage import reset_db, validate_db_and_schema

environ["DB_NAME"] = "labelizer-test"
environ["DB_SCHEMA"] = "labelizer-test"

# Be carefull to import the app_config after the environ variables are set, it should not have been imported before because then as it is a singleton the attributes will not change
from backend.config.app_config import app_config

Session = scoped_session(sessionmaker())
engine = create_engine(app_config.db_url)


@pytest.fixture(scope="session", autouse=True)
def db():
    validate_db_and_schema(engine)
    reset_db(engine)


@pytest.fixture(scope="function", autouse=True)
def session(db):
    session = Session()
    session.begin_nested()
    yield session
    session.rollback()
