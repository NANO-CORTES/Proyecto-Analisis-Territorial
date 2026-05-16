from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.recommendation import Base
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS recommendations"))
        conn.commit()
    Base.metadata.create_all(bind=engine)