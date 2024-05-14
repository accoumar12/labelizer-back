from pydantic import BaseModel

from labelizer.utils import SelectedItemType

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
        orm_mode = True


class LabelizedTriplet(BaseModel):
    reference_id: str
    left_id: str
    right_id: str
    # By default, the label is None, meaning that the user has not selected any option
    label: SelectedItemType = None
    # Same for the user_id
    user_id: str = None

    class Config:
        orm_mode = True
