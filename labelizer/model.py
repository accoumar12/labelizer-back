from dataclasses import dataclass
from enum import StrEnum


@dataclass
class LabelizerTripletResponse:
    request_id: str
    ref_id: str
    left_id: str
    right_id: str




class SelectedItemType(StrEnum):
    LEFT = 'left'
    RIGHT = 'right'
    NEITHER = 'neither'
    BOTH = 'both'


@dataclass
class TripletLabelized:
    id: str
    ref_id: str
    left_id: str
    right_id: str
    label: SelectedItemType | None  = None
    user_id: str | None = None