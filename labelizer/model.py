from dataclasses import dataclass
from enum import StrEnum


@dataclass
class LabelizerTripletResponse:
    request_id: str
    reference_id: str
    left_id: str
    right_id: str

class SelectedItemType(StrEnum):
    LEFT = 'left'
    RIGHT = 'right'
    NEITHER = 'neither'
    BOTH = 'both'
    #? Add an option if the two left and right items tend to be the most similar

@dataclass
class LabelizedTriplet:
    id: str
    reference_id: str
    left_id: str
    right_id: str
    label: SelectedItemType | None  = None
    user_id: str | None = None