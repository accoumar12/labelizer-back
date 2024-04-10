from enum import Enum

from pydantic import BaseModel


class SelectedItemType(str, Enum):
    LEFT = 'left'
    RIGHT = 'right'
    NEITHER = 'neither'
    BOTH = 'both'

class LabelizerPairsResponse(BaseModel):
    request_id: str
    reference_id: str
    left_id: str
    right_id: str 
    
    class Config:
        orm_mode = True

class TripletLabelized(BaseModel):
    reference_id: str
    left_id: str
    right_id: str
    label: SelectedItemType
    user_id: str

    class Config:
        orm_mode = True
