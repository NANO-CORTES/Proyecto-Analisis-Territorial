from fastapi import FastAPI
from app.core.database import engine, Base, get_db
from sqlalchemy import text
from app.api.endpoints import auth, users, health
from app.models.user import User, UserRole
from app.core.security import getPasswordHash
from app.repositories.user_repository import UserRepository
import time

with engine.connect() as con:
    con.execute(text("CREATE SCHEMA IF NOT EXISTS auth"))
    con.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth Service")


@app.on_event("startup")
def createInitialData():
    try:
        with engine.connect() as con:
            con.execute(text("ALTER TABLE auth.users ADD COLUMN IF NOT EXISTS username VARCHAR UNIQUE"))
            con.commit()
    except Exception:
        pass

    db = next(get_db())
    repo = UserRepository(db)
    adminExists = repo.getByEmail("admin@territorial.com")
    if not adminExists:
        adminUser = User(
            email="admin@territorial.com",
            username="admin",
            password_hash=getPasswordHash("admin123"),
            full_name="System Admin",
            role=UserRole.ADMIN,
            is_active=True,
        )
        repo.create(adminUser)


app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, prefix="/admin/users", tags=["admin"])
app.include_router(health.router)


@app.get("/health-check")
def healthCheck():
    try:
        with engine.connect() as con:
            con.execute(text("SELECT 1"))
        dbConnected = True
    except Exception:
        dbConnected = False

    return {
        "status": "healthy" if dbConnected else "unhealthy",
        "service_name": "ms-auth",
        "version": "1.0.0",
        "db_connected": dbConnected,
        "timestamp": int(time.time()),
    }
