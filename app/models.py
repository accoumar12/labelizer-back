from enum import Enum

from pydantic import BaseModel


class SelectedItemType(str, Enum):
    LEFT = 'left'
    RIGHT = 'right'
    NEITHER = 'neither'
    BOTH = 'both'

class LabelizerPairsResponse(BaseModel):
    id: int
    request_id: str
    reference_id: str
    left_id: str
    right_id: str

class TripletLabelized(BaseModel):
    id: int
    reference_id: str
    left_id: str
    right_id: str
    label: SelectedItemType = None
    user_id: str = None