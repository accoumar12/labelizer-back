import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "AppConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        workspace_dir = Path(os.environ["WORKSPACE_DIR"])
        self.images_path = workspace_dir / "data" / "images"

        self.dev_mod = bool(os.environ.get("DEV_MOD", False))

        self.db_user = os.environ["DB_USER"]
        self.db_password = os.environ["DB_PASSWORD"]
        self.db_host = os.environ["DB_HOST"]
        self.db_port = os.environ["DB_PORT"]
        self.db_name = os.environ["DB_NAME"]
        self.db_schema = os.environ["DB_SCHEMA"]

        self.lock_timeout_in_seconds = 30
        self.vector_dimension = 1280


app_config = AppConfig()
