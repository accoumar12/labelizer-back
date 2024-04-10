from pathlib import Path

from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse

import database.crud
import database.models
import database.schemas
from database.init_database import SessionLocal, engine

app = FastAPI()

database.models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



# @app.get('/api/labelizer/pairs')
# def get_labelizer_pairs(user_id: str) -> LabelizerPairsResponse:
#     # todo generate pairs
#     return LabelizerPairsResponse(
#         request_id='request_id',
#         reference_id='reference_id',
#         left_id='left_id',
#         right_id='right_id',
#     )

# @app.get('/api/labelizer/images/{image_id}')
# def get_image(user_id: str, image_id: str) -> FileResponse:
#     image_path = Path(f'/images/{image_id}.png')
#     if not image_path.exists():
#         raise HTTPException(status_code=404, detail='Image not found')
#     return FileResponse(str(image_path))

# @app.post('/api/labelizer/pairs')
# def set_labelizer_pairs(user_id: str, request_id: str = Form(), label: SelectedItemType = Form()) -> None:
#     # todo store selected ref with selected id
#     ...

