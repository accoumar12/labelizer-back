from pathlib import Path

import pandas as pd

from backend.utils import logger


def load_items(data_path: Path) -> pd.DataFrame:
    try:
        items = pd.read_csv(data_path)
        # We want to convert the string of the vector to a list of floats
        # items["vector"] = (
        #     items["vector"].str.split(",").apply(lambda x: list(map(float, x)))
        # )

    except FileNotFoundError as e:
        logger.info("File not found: %s", e)
        return pd.DataFrame()

    else:
        return items
