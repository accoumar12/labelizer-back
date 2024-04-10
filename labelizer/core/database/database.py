import os
import sqlite3
from pathlib import Path

database_root_path = Path(os.environ['DATABASE_ROOT_PATH'])

class DatabaseConnection:
    def __enter__(self):
        self.conn = sqlite3.connect(f'{database_root_path}/my_database.db')
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

def get_db():
    return DatabaseConnection()