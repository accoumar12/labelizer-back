from enum import Enum


class SelectedItemType(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    DONT_KNOW = "dont_know"
    # ? Add an option if the two left and right items tend to be the most similar, make it more complex for the next iteration


class UploadStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
