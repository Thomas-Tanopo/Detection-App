from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
import bcrypt
from app.database import get_db
from app.models.user import User
from app.jinja_setup import templates

router = APIRouter(prefix="/auth", tags=["auth"])

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return db.query(User).filter(User.id == user_id).first()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "auth/login.html")

@router.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(request, "auth/login.html", {
            "error": "Username atau password salah"
        })
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse(request, "auth/register.html")

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    if len(password) < 6:
        return templates.TemplateResponse(request, "auth/register.html", {
            "error": "Password minimal 6 karakter"
        })
    if db.query(User).filter(User.username == username).first():
        return templates.TemplateResponse(request, "auth/register.html", {
            "error": "Username sudah digunakan"
        })
    if db.query(User).filter(User.email == email).first():
        return templates.TemplateResponse(request, "auth/register.html", {
            "error": "Email sudah digunakan"
        })

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name
    )
    db.add(user)
    db.commit()
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=302)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/auth/login", status_code=302)
