from __future__ import annotations

from pydantic import BaseModel

from labelizer.types import SelectedItemType

# This file contains the Pydantic models, while the models file contains the SQLAlchemy models


class LabelizerTripletResponse(BaseModel):
    id: int
    reference_id: str
    reference_length: float
    left_id: str
    left_length: float
    right_id: str
    right_length: float

    class Config:
        from_attributes = True


class LabelizerValidationTripletResponse(BaseModel):
    id: int
    reference_id: str
    reference_length: float
    left_id: str
    left_length: float
    left_encoder_id: str
    right_id: str
    right_length: float
    right_encoder_id: str

    class Config:
        from_attributes = True


class LabelizedTriplet(BaseModel):
    reference_id: str
    reference_length: float
    left_id: str
    left_length: float
    right_id: str
    right_length: float
    encoder_id: str
    # By default, the label is None, meaning that the user has not selected any option
    label: SelectedItemType | None = None
    # Same for the user_id
    user_id: str | None = None

    class Config:
        from_attributes = True


class ValidationTriplet(BaseModel):
    reference_id: str
    reference_length: float
    left_id: str
    left_length: float
    left_encoder_id: str
    right_id: str
    right_length: float
    right_encoder_id: str
    label: SelectedItemType | None = None
    user_id: str | None = None

    class Config:
        from_attributes = True


class TripletStats(BaseModel):
    labeled: int
    unlabeled: int
    validation_labeled: int
    validation_unlabeled: int
