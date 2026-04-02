from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware # 1. IMPORTAR ESTO
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import engine, Base, get_db
from app.services.auth import get_user_by_username, create_user
from app.core.security import verify_password, create_access_token
from app.schemas.user import Token, UserCreate
from app.models.user import User
from sqlalchemy import text

# Create schema if not exists
with engine.connect() as con:
    con.execute(text("CREATE SCHEMA IF NOT EXISTS configuration"))
    con.commit()

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Configuration Service")

# 2. AÑADIR ESTE BLOQUE DE CORS (CRÍTICO)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite peticiones desde cualquier origen (8001, 8000, etc)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service_name": "ms-configuration"}

@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_username(db, user.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")
    return create_user(db, user)