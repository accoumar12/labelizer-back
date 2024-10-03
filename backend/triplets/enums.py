from enum import Enum


class SelectedItemType(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    DONT_KNOW = "dont_know"
