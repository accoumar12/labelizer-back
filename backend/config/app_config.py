import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    def __init__(self) -> None:
        self.setup_config()

    def setup_config(self) -> None:
        workspace_dir = Path(os.environ["WORKSPACE_DIR"])
        self.images_path = workspace_dir / "data" / "images"

        self.dev_mod = bool(os.environ.get("DEV_MOD", False))

        db_user = os.environ["DB_USER"]
        db_password = os.environ["DB_PASSWORD"]
        db_host = os.environ["DB_HOST"]
        db_port = os.environ["DB_PORT"]
        self.db_name = os.environ["DB_NAME"]
        self.db_url = (
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{self.db_name}"
        )
        self.db_schema = os.environ["DB_SCHEMA"]

        self.lock_timeout_in_seconds = 30
        self.vector_dimension = 1280


app_config = AppConfig()
