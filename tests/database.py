from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config.app_config import app_config

test_engine = create_engine(app_config.db_url)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
