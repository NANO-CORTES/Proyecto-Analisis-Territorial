from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    # hu-15
    from app.models.ranking import Base as RankingBase
    
    # Esta es la "llave" para que el puerto 8005 no se bloquee
    with engine.connect() as connection:
        connection.execute(text("CREATE SCHEMA IF NOT EXISTS analytics"))
        connection.commit()
    
    # Crea las tablas de Analítica sin tocar las de los otros servicios
    Base.metadata.create_all(bind=engine)
    RankingBase.metadata.create_all(bind=engine)