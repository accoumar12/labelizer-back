from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config.app_config import app_config

engine = create_engine(app_config.db_url)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
