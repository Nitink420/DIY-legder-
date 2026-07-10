from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os

router = APIRouter()

# Simple request schema for login
class LoginRequest(BaseModel):
    username: str
    password: str

# Configurable admin credentials
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "scrapk2026")
SECURE_TOKEN = os.getenv("SESSION_TOKEN", "secure-scrapk-session-token-2026")

@router.post("/auth/login")
def login(payload: LoginRequest):
    if payload.username == ADMIN_USERNAME and payload.password == ADMIN_PASSWORD:
        return {
            "status": "success",
            "token": SECURE_TOKEN,
            "username": ADMIN_USERNAME
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

# Dependency helper to verify authorization token
def verify_token(authorization: str = None):
    # Standard header is usually "Bearer <token>"
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )
    
    token = authorization.replace("Bearer ", "").strip()
    if token != SECURE_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authorization token"
        )
    return token
