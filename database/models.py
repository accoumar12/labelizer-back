from enum import Enum

from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


# Useful type to labelize the triplet
class SelectedItemType(str, Enum):
    LEFT = 'left'
    RIGHT = 'right'
    NEITHER = 'neither'
    BOTH = 'both'

class LabelizerPairsResponse(Base):
    __tablename__ = 'labelizer_pairs'
    
    id = Column(Integer, primary_key=True, index=True)
    #? Request ID is unique
    request_id = Column(String, index=True)
    reference_id = Column(String, index=True)
    left_id = Column(String, index=True)
    right_id = Column(String, index=True)

class TripletLabelized(Base):
    __tablename__ = 'triplet_labelized'
    
    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, index=True)
    left_id = Column(String, index=True)
    right_id = Column(String, index=True)
    label = Column(SelectedItemType, index=True)
    user_id = Column(String, index=True)