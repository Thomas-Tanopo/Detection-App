from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.routers.auth import get_current_user
from app.jinja_setup import templates

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("", response_class=HTMLResponse)
async def list_categories(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    categories = db.query(Category).order_by(Category.created_at.desc()).all()
    return templates.TemplateResponse(request, "categories/list.html", {
        "user": user,
        "categories": categories
    })

@router.get("/create", response_class=HTMLResponse)
async def create_category_page(
    request: Request,
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse(request, "categories/form.html", {
        "user": user,
        "category": None
    })

@router.post("/create")
async def create_category(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    return RedirectResponse(url="/categories", status_code=302)

@router.get("/{id}/edit", response_class=HTMLResponse)
async def edit_category_page(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return templates.TemplateResponse(request, "categories/form.html", {
        "user": user,
        "category": category
    })

@router.post("/{id}/edit")
async def edit_category(
    request: Request,
    id: int,
    name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    category = db.query(Category).filter(Category.id == id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.name = name
    category.description = description
    db.commit()
    return RedirectResponse(url="/categories", status_code=302)

@router.get("/{id}/delete")
async def delete_category(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    category = db.query(Category).filter(Category.id == id).first()
    if category:
        db.delete(category)
        db.commit()
    return RedirectResponse(url="/categories", status_code=302)
