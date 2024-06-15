from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from labelizer.app_config import AppConfig

app_config = AppConfig()

SQLALCHEMY_DATABASE_URL = app_config.db_url


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
