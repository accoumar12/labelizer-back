from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config.config import config

test_engine = create_engine(config.db_url)
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
