from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core import security
from app.core.database import get_db
from app.interfaces.user_repository import IUserRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserResponse

router = APIRouter()


def _getUserRepo(db: Session = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)


@router.post("/login", response_model=Token)
def login(
    formData: OAuth2PasswordRequestForm = Depends(),
    repo: IUserRepository = Depends(_getUserRepo),
):
    user = repo.getByEmailOrUsername(formData.username, formData.username)
    if not user or not security.verifyPassword(formData.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")

    accessToken = security.createAccessToken(user.email, role=user.role.value)
    refreshToken = security.createRefreshToken(user.email)

    user.last_login = datetime.now(timezone.utc)
    repo.update(user)

    return {
        "access_token": accessToken,
        "refresh_token": refreshToken,
        "token_type": "bearer",
    }


@router.post("/register", response_model=UserResponse)
def register(
    userIn: UserCreate,
    repo: IUserRepository = Depends(_getUserRepo),
):
    userExists = repo.getByEmailOrUsername(userIn.email, userIn.username)
    if userExists:
        raise HTTPException(status_code=400, detail="El correo o el nombre de usuario ya esta en uso.")

    newUser = User(
        email=userIn.email,
        username=userIn.username,
        full_name=userIn.full_name or userIn.username,
        password_hash=security.getPasswordHash(userIn.password),
        role=userIn.role,
        is_active=True,
    )
    return repo.create(newUser)


@router.post("/logout")
def logout():
    return {"message": "Has cerrado sesion correctamente"}
