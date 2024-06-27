import logging

from sqlalchemy import text

from backend.config.app_config import app_config
from backend.core.database.core import Base, SessionLocal

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()


def delete_all_tables(engine) -> None:
    with engine.connect() as connection:
        for table in Base.metadata.sorted_tables:
            connection.execute(
                text(f"DROP TABLE IF EXISTS {table.fullname} CASCADE;"),
            )


def init_db(engine) -> None:
    with engine.connect() as connection:
        # We have moved the creation of the database and schema to separate scripts
        result = connection.execute(
            text(
                f"SELECT datname FROM pg_database WHERE datname = '{app_config.db_name}';",
            ),
        )
        db_name = result.scalar()
        if db_name == app_config.db_name:
            logger.info("Database %s used", app_config.db_name)
        else:
            msg = f"Database {app_config.db_name} does not exist"
            raise Exception(msg)
        result = connection.execute(
            text(
                f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{app_config.db_schema}';",
            ),
        )
        schema_name = result.scalar()
        if schema_name == app_config.db_schema:
            logger.info("Schema %s used", app_config.db_schema)
        else:
            msg = f"Schema {app_config.db_schema} does not exist"
            raise Exception(msg)

        Base.metadata.create_all(bind=engine)


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
