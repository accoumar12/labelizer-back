import logging

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy_utils import database_exists

from labelizer.config.app_config import app_config

# For this logger, we have to specify the config otherwise we do not see anything logged
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


SQL_ALCHEMY_DB_URL = app_config.db_url

engine = create_engine(SQL_ALCHEMY_DB_URL)


# We move the creation of the database to other scripts
if not database_exists(SQL_ALCHEMY_DB_URL):
    msg = f"Database {app_config.db_name} does not exist"
    raise Exception(msg)

# with engine.connect() as conn:
#     result = conn.execute(
#         text("SELECT extname FROM pg_extension WHERE extname = 'vector';"),
#     )
#     extension_name = (
#         result.scalar()
#     )  # Will return None if there is no row in the result
#     if extension_name == "vector":
#         logger.info("Extension 'vector' is installed")
#     else:
#         msg = "Extension 'vector' is not installed."
#         raise Exception(msg)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We refer to https://docs.sqlalchemy.org/en/14/orm/declarative_tables.html#explicit-schema-name-with-declarative-table for specifying the schema name
Base = declarative_base(metadata=MetaData(schema=app_config.db_schema))
