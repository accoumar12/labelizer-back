from backend.config.app_config import AppConfig
from backend.core.database.core import Base
from sqlalchemy import Column, Float, String

app_config = AppConfig()


class Item(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True, index=True)
    length = Column(Float, index=True)
    dataset = Column(String, index=True)
    # vector = Column(Vector(app_config.vector_dimension))
