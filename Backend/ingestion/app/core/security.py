from typing import Dict
from jose import jwt, JWTError
from fastapi import HTTPException, Security, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()


def decodeAccessToken(token: str) -> Dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def getCurrentUser(credentials: HTTPAuthorizationCredentials = Security(security)) -> Dict:
    payload = decodeAccessToken(credentials.credentials)
    username = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    return {"username": username, "role": payload.get("role")}


def requireRole(allowedRoles: list[str]):
    def roleChecker(request: Request, user: dict = Depends(getCurrentUser)):
        if user.get("role") not in allowedRoles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        request.state.user = user
        return user
    return roleChecker
