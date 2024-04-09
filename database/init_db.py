from sqlalchemy import Column, Enum, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .models import SelectedItemType

Base = declarative_base()

class LabelizerPairs(Base):
    __tablename__ = "labelizer_pairs"

    request_id = Column(String, primary_key=True)
    reference_id = Column(String)
    left_id = Column(String)
    right_id = Column(String)

class TripletLabelized(Base):
    __tablename__ = "triplet_labelized"

    id = Column(String, primary_key=True)
    reference_id = Column(String)
    left_id = Column(String)
    right_id = Column(String)
    label = Column(Enum(SelectedItemType))
    user_id = Column(String)

def init_db():
    engine = create_engine('sqlite:///./test.db', echo=True)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()

if __name__ == "__main__":
    init_db()