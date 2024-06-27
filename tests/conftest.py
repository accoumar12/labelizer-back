import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from starlette.config import environ

environ["DB_NAME"] = "labelizer-test"
environ["DB_SCHEMA"] = "labelizer-test"

# Be carefull to import the app_config after the environ variables are set, it should not have been imported before because then the attributes will not be correct
# Also be careful not to import modules that would instantiate the app_config before the environ variables are set, life manage
from backend.config.app_config import app_config
from backend.core.database.manage import delete_all_tables, init_db

Session = scoped_session(sessionmaker())
engine = create_engine(app_config.db_url)


@pytest.fixture(scope="session")
def db():
    delete_all_tables(engine)
    init_db(engine)


@pytest.fixture(scope="function", autouse=True)
def session(db):
    session = Session()
    session.begin_nested()
    yield session
    session.rollback()
