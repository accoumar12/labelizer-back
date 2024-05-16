import io
import shutil
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from labelizer import crud
from labelizer.app_config import AppConfig

app_config = AppConfig()


def get_db_excel_export(db: Session) -> io.BytesIO:
    data = crud.get_all_data(db)
    data = pd.DataFrame(data)
    stream = io.BytesIO()
    data.to_excel(stream, index=False)
    stream.seek(0)
    return stream


def update_database(
    db: Session,
    triplets: pd.DataFrame,
    validation_triplets: pd.DataFrame,
    uploaded_images_path: Path,
) -> None:
    crud.create_labelized_triplets(db, triplets)
    crud.create_validation_triplets(db, validation_triplets)
    uploaded_images = uploaded_images_path.iterdir()
    for file in uploaded_images:
        destination = app_config.images_path / file.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(file, destination)
