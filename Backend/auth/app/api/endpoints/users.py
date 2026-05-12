from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.interfaces.user_repository import IUserRepository
from app.repositories.user_repository import UserRepository

router = APIRouter()


def _getUserRepo(db: Session = Depends(get_db)) -> IUserRepository:
    return UserRepository(db)


def getCurrentUser(db: Session = Depends(get_db), authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No autorizado")
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalido")

    repo = UserRepository(db)
    user = repo.getByEmail(email)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


def getCurrentAdminUser(currentUser: User = Depends(getCurrentUser)):
    if currentUser.role != UserRole.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado: se requiere rol ADMIN")
    return currentUser


@router.get("/me", response_model=UserResponse)
def readUserMe(currentUser: User = Depends(getCurrentUser)):
    return currentUser


@router.get("/", response_model=List[UserResponse])
def readUsers(
    skip: int = 0,
    limit: int = 100,
    currentAdmin: User = Depends(getCurrentAdminUser),
    repo: IUserRepository = Depends(_getUserRepo),
):
    return repo.getAll(skip, limit)


@router.post("/", response_model=UserResponse)
def createUser(
    userIn: UserCreate,
    currentAdmin: User = Depends(getCurrentAdminUser),
    repo: IUserRepository = Depends(_getUserRepo),
):
    user = repo.getByEmail(userIn.email)
    if user:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con este email")

    userData = userIn.dict()
    password = userData.pop("password")
    userData["password_hash"] = security.getPasswordHash(password)

    user = User(**userData)
    return repo.create(user)


@router.patch("/{userId}", response_model=UserResponse)
def updateUser(
    userId: int,
    userIn: UserUpdate,
    currentAdmin: User = Depends(getCurrentAdminUser),
    repo: IUserRepository = Depends(_getUserRepo),
):
    user = repo.getById(userId)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if userId == currentAdmin.id and userIn.is_active is False:
        raise HTTPException(status_code=400, detail="Un administrador no puede desactivar su propia cuenta")

    updateData = userIn.dict(exclude_unset=True)
    if "password" in updateData:
        password = updateData.pop("password")
        user.password_hash = security.getPasswordHash(password)

    for field in updateData:
        setattr(user, field, updateData[field])

    return repo.update(user)


@router.delete("/{userId}", response_model=UserResponse)
def deleteUser(
    userId: int,
    currentAdmin: User = Depends(getCurrentAdminUser),
    repo: IUserRepository = Depends(_getUserRepo),
):
    user = repo.getById(userId)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if userId == currentAdmin.id:
        raise HTTPException(status_code=400, detail="Un administrador no puede eliminarse a si mismo")

    user.is_active = False
    return repo.update(user)
