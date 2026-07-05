from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.item import Item
from app.models.category import Category
from app.routers.auth import get_current_user
from app.jinja_setup import templates

router = APIRouter(prefix="/items", tags=["items"])

@router.get("", response_class=HTMLResponse)
async def list_items(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    items = db.query(Item).order_by(Item.created_at.desc()).all()
    return templates.TemplateResponse(request, "items/list.html", {
        "user": user,
        "items": items
    })

@router.get("/create", response_class=HTMLResponse)
async def create_item_page(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    categories = db.query(Category).order_by(Category.name).all()
    return templates.TemplateResponse(request, "items/form.html", {
        "user": user,
        "item": None,
        "categories": categories
    })

@router.post("/create")
async def create_item(
    request: Request,
    name: str = Form(...),
    description: str = Form(None),
    category_id: int = Form(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    item = Item(name=name, description=description, category_id=category_id)
    db.add(item)
    db.commit()
    return RedirectResponse(url="/items", status_code=302)

@router.get("/{id}/edit", response_class=HTMLResponse)
async def edit_item_page(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    categories = db.query(Category).order_by(Category.name).all()
    return templates.TemplateResponse(request, "items/form.html", {
        "user": user,
        "item": item,
        "categories": categories
    })

@router.post("/{id}/edit")
async def edit_item(
    request: Request,
    id: int,
    name: str = Form(...),
    description: str = Form(None),
    category_id: int = Form(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    item = db.query(Item).filter(Item.id == id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item.name = name
    item.description = description
    item.category_id = category_id
    db.commit()
    return RedirectResponse(url="/items", status_code=302)

@router.get("/{id}/delete")
async def delete_item(
    request: Request,
    id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    item = db.query(Item).filter(Item.id == id).first()
    if item:
        db.delete(item)
        db.commit()
    return RedirectResponse(url="/items", status_code=302)
