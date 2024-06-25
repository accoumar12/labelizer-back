import logging

from sqlalchemy_utils import database_exists

from labelizer.config.app_config import app_config
from labelizer.core.database.core import SessionLocal

logger = logging.getLogger()


def init_database() -> None:
    # We move the creation of the database to other scripts
    if not database_exists(app_config.db_url):
        msg = f"Database {app_config.db_name} does not exist"
        raise Exception(msg)
    logger.info("Database %s exists", app_config.db_name)


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
