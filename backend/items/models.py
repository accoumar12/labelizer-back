from sqlalchemy import Column, Float, String

from backend.core.database.core import Base


class Item(Base):
    __tablename__ = "item"
    id = Column(String, primary_key=True, index=True)
    length = Column(Float, index=True)
    dataset = Column(String, index=True)
    # vector = Column(Vector(app_config.vector_dimension))
