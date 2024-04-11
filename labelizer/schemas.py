from pydantic import BaseModel

from labelizer.utils import SelectedItemType


class LabelizerTripletResponse(BaseModel):
    id: str
    reference_id: str
    left_id: str
    right_id: str 
    
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
