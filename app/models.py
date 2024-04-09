from enum import Enum
from pydantic import BaseModel

class SelectedItemType(str, Enum):
    LEFT = 'left'
    RIGHT = 'right'
    NEITHER = 'neither'
    BOTH = 'both'

class LabelizerPairsResponse(BaseModel):
    request_id: str
    ref_id: str
    left_id: str
    right_id: str

class (BaseModel):
    id: str
    ref_id: str
    left_id: str
    right_id: str
    label: SelectedItemType = None
    user_id: str = None