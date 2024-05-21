from sqlalchemy import Column, Enum, Float, Integer, String

from labelizer.core.database.init_database import Base
from labelizer.types import SelectedItemType


class TripletBase(Base):
    # Use this class as an abstract base class for the other classes, so that SQLAlchemy doesn't create a table for it.
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, index=True)
    reference_length = Column(Float, index=True)
    left_id = Column(String, index=True)
    left_length = Column(Float, index=True)
    right_id = Column(String, index=True)
    right_length = Column(Float, index=True)
    label = Column(Enum(SelectedItemType), index=True)
    user_id = Column(String, index=True)

    # This method is used to convert the object to a dictionary, useful for retrieving the csv when we download the database
    def to_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in self.__table__.columns}


class LabelizedTriplet(TripletBase):
    __tablename__ = "labelized_triplets"

    encoder_id = Column(String, index=True)


class ValidationTriplet(TripletBase):
    __tablename__ = "validation_triplets"

    left_encoder_id = Column(String, index=True)
    right_encoder_id = Column(String, index=True)
