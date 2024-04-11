import enum

from database.init_database import Base
from sqlalchemy import Column, Enum, Integer, String


class SelectedItemType(enum.Enum):
    LEFT = 'left'
    RIGHT = 'right'
    DONT_KNOW = 'dont_know'
    #? Add an option if the two left and right items tend to be the most similar, make it more complex for the next iteration

class LabelizerTripletResponse:
    request_id: str
    reference_id: str
    left_id: str
    right_id: str

class LabelizedTriplet(Base):
    __tablename__ = 'labelized_triplets'
    
    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, index=True)
    left_id = Column(String, index=True)
    right_id = Column(String, index=True)
    label = Column(Enum(SelectedItemType), index=True)
    user_id = Column(String, index=True)
