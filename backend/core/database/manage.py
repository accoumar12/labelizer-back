import logging

from backend.core.database.core import Base, SessionLocal

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()


def drop_all_tables(engine) -> None:
    Base.metadata.drop_all(bind=engine)


def create_all_tables(engine) -> None:
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
