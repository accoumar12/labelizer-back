from labelizer.core.database.init_database import SessionLocal


def get_db() -> SessionLocal:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
