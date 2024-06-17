from __future__ import annotations

# Be careful not to move into a type checking block because in this case pydantic will not be able to find the datetime module !
import datetime  # noqa: TCH003

from pydantic import BaseModel

from labelizer.triplets.enums import SelectedItemType


class TripletBase(BaseModel):
    reference_id: str
    left_id: str
    right_id: str

    class Config:
        from_attributes = True


class LabelizerTripletResponse(TripletBase):
    id: int
    reference_length: float
    left_length: float
    right_length: float


class LabelizerValidationTripletResponse(TripletBase):
    id: int
    reference_length: float
    left_length: float
    right_length: float
    left_encoder_id: str
    right_encoder_id: str


class LabeledTriplet(TripletBase):
    encoder_id: str
    label: SelectedItemType | None = None
    user_id: str | None = None
    retrieved_at: datetime.datetime | None = None


class TripletStats(BaseModel):
    labeled: int
    unlabeled: int
    validation_labeled: int
    validation_unlabeled: int


class TripletsUploadStatus(BaseModel):
    id: int
    to_upload_triplets_count: int = 0
    uploaded_triplets_count: int


class ValidationTriplet(TripletBase):
    left_encoder_id: str
    right_encoder_id: str
    label: SelectedItemType | None = None
    user_id: str | None = None
    retrieved_at: datetime.datetime | None = None
