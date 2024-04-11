from sqlalchemy import Column, Enum, Integer, String

from labelizer.core.database.init_database import Base
from labelizer.utils import SelectedItemType


class LabelizedTriplet(Base):
    __tablename__ = 'labelized_triplets'
    
    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String, index=True)
    left_id = Column(String, index=True)
    right_id = Column(String, index=True)
    # By default, the label is None, meaning that the user has not selected any option
    label = Column(Enum(SelectedItemType), index=True)
    # Same for the user_id
    user_id = Column(String, index=True)
