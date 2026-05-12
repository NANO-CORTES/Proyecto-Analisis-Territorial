import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _preHashPassword(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:
    return pwdContext.verify(_preHashPassword(plainPassword), hashedPassword)


def getPasswordHash(password: str) -> str:
    return pwdContext.hash(_preHashPassword(password))


def createAccessToken(subject: Union[str, Any], role: str = "USER", expiresDelta: timedelta = None) -> str:
    if expiresDelta:
        expire = datetime.now(timezone.utc) + expiresDelta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    toEncode = {"exp": expire, "sub": str(subject), "role": role}
    return jwt.encode(toEncode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def createRefreshToken(subject: Union[str, Any]) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    toEncode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(toEncode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
