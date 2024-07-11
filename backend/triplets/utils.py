from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from fastapi import HTTPException, status

from backend.utils import logger

if TYPE_CHECKING:
    from pathlib import Path


def load_triplets(data_path: Path) -> pd.DataFrame:
    try:
        return pd.read_csv(data_path)
    except FileNotFoundError as e:
        logger.info("File not found: %s", e)
        return pd.DataFrame()


def extract_triplets_ids(triplets: pd.DataFrame) -> set[str]:
    """Extract a set of triplet IDs from a DataFrame."""
    return set(
        triplets[["reference_id", "left_id", "right_id"]].to_numpy().flatten(),
    )


def check_match_triplets_images(
    triplets_ids: set[str],
    all_images_ids: set[str],
) -> None:
    missing_images_names = triplets_ids - all_images_ids
    if missing_images_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing images for these ids: {missing_images_names}.",
        )
