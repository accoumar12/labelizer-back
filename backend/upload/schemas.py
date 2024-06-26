from pydantic import BaseModel


class AllTripletsUploadStatus(BaseModel):
    id: int
    to_upload_all_triplets_count: int = 0
    uploaded_all_triplets_count: int
