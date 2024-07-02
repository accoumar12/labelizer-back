from sqlalchemy import Column, Integer

from backend.core.database.core import Base


class AllTripletsUploadStatus(Base):
    __tablename__ = "all_triplets_upload_status"

    id = Column(Integer, primary_key=True, index=True)
    to_upload_count = Column(Integer, index=True)
    uploaded_count = Column(Integer, index=True)
