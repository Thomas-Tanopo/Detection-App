from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import bcrypt
from app.database import get_db
from app.models.user import User
from app.auth_jwt import create_access_token, get_current_user

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    full_name: str = ""

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not bcrypt.checkpw(req.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Username atau password salah")
    token = create_access_token({"user_id": user.id})
    return AuthResponse(access_token=token, user={
        "id": user.id, "username": user.username, "full_name": user.full_name, "email": user.email
    })

@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if len(req.password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password minimal 6 karakter")
    if db.query(User).filter((User.username == req.username) | (User.email == req.email)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username atau email sudah terdaftar")
    pwd = bcrypt.hashpw(req.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user = User(username=req.username, email=req.email, password_hash=pwd, full_name=req.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"user_id": user.id})
    return AuthResponse(access_token=token, user={
        "id": user.id, "username": user.username, "full_name": user.full_name, "email": user.email
    })

@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "username": user.username, "full_name": user.full_name, "email": user.email}
