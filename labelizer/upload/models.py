from sqlalchemy import Column, Integer

from labelizer.core.database.core import Base


class AllTripletsUploadStatus(Base):
    __tablename__ = "all_triplets_upload_statuses"

    id = Column(Integer, primary_key=True, index=True)
    to_upload_all_triplets_count = Column(Integer, index=True)
    uploaded_all_triplets_count = Column(Integer, index=True)
