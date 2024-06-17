import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from labelizer.config.app_config import AppConfig

app_config = AppConfig()

SQLALCHEMY_DATABASE_URL = app_config.db_url

# For this logger, we have to specify the config otherwise we do not see anything logged
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)

with engine.connect() as conn:
    result = conn.execute(
        text("SELECT extname FROM pg_extension WHERE extname = 'vector';"),
    )
    extension_name = (
        result.scalar()
    )  # Will return None if there is no row in the result
    if extension_name == "vector":
        logger.info("Extension 'vector' is installed")
    else:
        msg = "Extension 'vector' is not installed."
        raise Exception(msg)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
