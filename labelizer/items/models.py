from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Float, String

from labelizer.config.app_config import AppConfig
from labelizer.core.database.init_database import Base

app_config = AppConfig()


class Item(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True, index=True)
    length = Column(Float, index=True)
    scope = Column(String, index=True)
    # Be careful to remove the index here, otherwise we can not load the data (too large for b-tree index) !
    vector = Column(Vector(app_config.vector_dimension))
