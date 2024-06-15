from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from labelizer.app_config import AppConfig
from labelizer.core.database.init_database import Base
from labelizer.types import SelectedItemType

app_config = AppConfig()


class TripletBase(Base):
    # Use this class as an abstract base class for the other classes, so that SQLAlchemy doesn't create a table for it.
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, ForeignKey("items.id"), index=True)
    left_id = Column(String, ForeignKey("items.id"), index=True)
    right_id = Column(String, ForeignKey("items.id"), index=True)
    label = Column(Enum(SelectedItemType), index=True)
    user_id = Column(String, index=True)
    # We add a "retrieved_at" column to manage the locking of the triplets, so two users will not deal with the same triplet
    retrieved_at = Column(DateTime(timezone=True), index=True)

    # This method is used to convert the object to a dictionary, useful for retrieving the csv when we download the database
    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

    @declared_attr
    def reference_item(cls):
        return relationship("Item", foreign_keys=[cls.reference_id])

    @declared_attr
    def left_item(cls):
        return relationship("Item", foreign_keys=[cls.left_id])

    @declared_attr
    def right_item(cls):
        return relationship("Item", foreign_keys=[cls.right_id])


class LabeledTriplet(TripletBase):
    __tablename__ = "labeled_triplets"

    encoder_id = Column(String, index=True)


class ValidationTriplet(TripletBase):
    __tablename__ = "validation_triplets"

    left_encoder_id = Column(String, index=True)
    right_encoder_id = Column(String, index=True)


class TripletUploadStatus(Base):
    __tablename__ = "triplets_upload_status"

    id = Column(Integer, primary_key=True, index=True)
    to_upload_triplets_count = Column(Integer, index=True)
    uploaded_triplets_count = Column(Integer, index=True)


class Item(Base):
    __tablename__ = "items"
    id = Column(String, primary_key=True, index=True)
    length = Column(Float, index=True)
    vector = Column(Vector(app_config.vector_dimension), index=True)
