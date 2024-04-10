import gzip
import json
import logging
import os
import shutil
import sqlite3


SQLITE_IN_MEMORY = ":memory:"

_sqlite_conn = None

logger = logging.getLogger(__name__)


def get_sqlite_conn(reset: bool = False, host: str = None):
    global _sqlite_conn
    if reset and _sqlite_conn:
        _sqlite_conn.close()
        _sqlite_conn = None

    if _sqlite_conn is None:
        app_config = get_app_config()
        if not host:
            host = app_config.dashboard_sqlite_host

        if host == SQLITE_IN_MEMORY:
            uri = SQLITE_IN_MEMORY
        else:
            mode = app_config.dashboard_sqlite_mode
            uri = f"{host}?mode={mode}"

        local_conn = get_sqlite3_connection("file:" + uri)
        if copy_in_memory:
            logger.info("Loading database in memory...")
            # WSL makes query execution very slow, so we load all db in memory.
            _sqlite_conn = sqlite3.connect(':memory:', check_same_thread=False)
            local_conn.backup(_sqlite_conn)
            local_conn.close()
            logger.info("Done.")
        else:
            _sqlite_conn = local_conn
    return _sqlite_conn


def get_sqlite3_connection(uri: str):
    return sqlite3.connect(uri, uri=True, check_same_thread=False)

