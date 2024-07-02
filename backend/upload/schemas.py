from pydantic import BaseModel


class AllTripletsUploadStatus(BaseModel):
    id: int
    to_upload_count: int = 0
    uploaded_count: int
