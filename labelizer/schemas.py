from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from labelizer.types import SelectedItemType

if TYPE_CHECKING:
    import datetime


class TripletBase(BaseModel):
    reference_id: str
    reference_length: float
    left_id: str
    left_length: float
    right_id: str
    right_length: float
    retrieved_at: datetime.datetime | None = None

    class Config:
        from_attributes = True


class LabelizerTripletResponse(TripletBase):
    id: int


class LabelizerValidationTripletResponse(TripletBase):
    id: int
    left_encoder_id: str
    right_encoder_id: str


class LabelizedTriplet(TripletBase):
    encoder_id: str
    label: SelectedItemType | None = None
    user_id: str | None = None


class ValidationTriplet(TripletBase):
    left_encoder_id: str
    right_encoder_id: str
    label: SelectedItemType | None = None
    user_id: str | None = None


class TripletStats(BaseModel):
    labeled: int
    unlabeled: int
    validation_labeled: int
    validation_unlabeled: int
