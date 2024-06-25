from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship

from labelizer.core.database.core import Base
from labelizer.triplets.enums import SelectedItemType


class TripletBase(Base):
    # Use this class as an abstract base class for the other classes, so that SQLAlchemy doesn't create a table for it.
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, ForeignKey("items.id"), index=True)
    left_id = Column(String, ForeignKey("items.id"), index=True)
    right_id = Column(String, ForeignKey("items.id"), index=True)
    # cf https://github.com/sqlalchemy/sqlalchemy/discussions/10583, we need to explicitly specify the schema for the Enum to be defined for this specific schema
    label = Column(Enum(SelectedItemType, inherit_schema=True), index=True)
    user_id = Column(String, index=True)
    # We add a "retrieved_at" column to manage the locking of the triplets, so two users will not deal with the same triplet
    retrieved_at = Column(DateTime(timezone=True), index=True)

    # This method is used to convert the object to a dictionary, useful for retrieving the csv when we download the database
    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}

    # We need to use the @declared_attr decorator to be able to use the relationships in the subclasses
    @declared_attr
    def reference_item(cls):
        return relationship("Item", foreign_keys=[cls.reference_id])

    @declared_attr
    def left_item(cls):
        return relationship("Item", foreign_keys=[cls.left_id])

    @declared_attr
    def right_item(cls):
        return relationship("Item", foreign_keys=[cls.right_id])


class Triplet(TripletBase):
    __tablename__ = "triplets"

    encoder_id = Column(String, index=True)


class ValidationTriplet(TripletBase):
    __tablename__ = "validation_triplets"

    left_encoder_id = Column(String, index=True)
    right_encoder_id = Column(String, index=True)
