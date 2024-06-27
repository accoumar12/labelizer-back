from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config.app_config import app_config

engine = create_engine(app_config.db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# We refer to https://docs.sqlalchemy.org/en/14/orm/declarative_tables.html#explicit-schema-name-with-declarative-table for specifying the schema name
class Base(DeclarativeBase):
    metadata = MetaData(schema=app_config.db_schema)
