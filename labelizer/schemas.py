from enum import Enum

from pydantic import BaseModel


class SelectedItemType(str, Enum):
    LEFT = 'left'
    RIGHT = 'right'
    DONT_KNOW = 'dont_know'
    #? Add an option if the two left and right items tend to be the most similar, make it more complex for the next iteration

class LabelizerTripletResponse(BaseModel):
    request_id: str
    reference_id: str
    left_id: str
    right_id: str 
    
    class Config:
        orm_mode = True

class LabelizedTriplet(BaseModel):
    reference_id: str
    left_id: str
    right_id: str
    label: SelectedItemType
    user_id: str

    class Config:
        orm_mode = True
