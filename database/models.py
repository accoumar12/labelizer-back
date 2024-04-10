import enum

from sqlalchemy import Boolean, Column, Enum, Integer, String
from sqlalchemy.orm import relationship

from database.init_database import Base


# Useful type to labelize the triplet
class SelectedItemType(enum.Enum):
    LEFT = 'left'
    RIGHT = 'right'
    NEITHER = 'neither'
    BOTH = 'both'
    #? Add a reverse option to the enum, if the left and right tend to be the ones that are the closest

# class LabelizerPairsResponse(Base):
#     __tablename__ = 'labelizer_pairs'
    
#     id = Column(Integer, primary_key=True, index=True)
#     #? Request ID is unique
#     request_id = Column(String, index=True)
#     reference_id = Column(String, index=True)
#     left_id = Column(String, index=True)
#     right_id = Column(String, index=True)

class LabelizedTriplet(Base):
    __tablename__ = 'labelized_triplets'
    
    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, index=True)
    left_id = Column(String, index=True)
    right_id = Column(String, index=True)
    label = Column(Enum(SelectedItemType), index=True)
    user_id = Column(String, index=True)