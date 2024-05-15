from sqlalchemy import Column, Enum, Float, Integer, String

from labelizer.core.database.init_database import Base
from labelizer.types import SelectedItemType

# This file contains the SQLAlchemy models, while the schemas file contains the Pydantic models


class LabelizedTriplet(Base):
    __tablename__ = "labelized_triplets"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, index=True)
    reference_length = Column(Float, index=True)
    left_id = Column(String, index=True)
    left_length = Column(Float, index=True)
    right_id = Column(String, index=True)
    right_length = Column(Float, index=True)
    # We include the id of the model used to generate the triplets
    model_id = Column(String, index=True)
    # By default, the label is None, meaning that the user has not selected any option. This is expressed in the pydantic schemas
    label = Column(Enum(SelectedItemType), index=True)
    # Same for the user_id
    user_id = Column(String, index=True)

    # This method is used to convert the object to a dictionary, useful for retrieving the csv when we download the database
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "reference_id": self.reference_id,
            "reference_length": self.reference_length,
            "left_id": self.left_id,
            "left_length": self.left_length,
            "right_id": self.right_id,
            "right_length": self.right_length,
            "model_id": self.model_id,
            "label": self.label,
            "user_id": self.user_id,
        }
