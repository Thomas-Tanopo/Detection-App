from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.auth_jwt import get_current_user
from app.models.user import User

router = APIRouter()

class CategoryCreate(BaseModel):
    name: str
    description: str = ""

@router.get("")
def list_categories(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    cats = db.query(Category).order_by(Category.created_at.desc()).all()
    return [{"id": c.id, "name": c.name, "description": c.description, "created_at": c.created_at.isoformat()} for c in cats]

@router.post("")
def create_category(data: CategoryCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = Category(name=data.name, description=data.description)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "name": c.name, "description": c.description, "created_at": c.created_at.isoformat()}

@router.get("/{id}")
def get_category(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Category).filter(Category.id == id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori tidak ditemukan")
    return {"id": c.id, "name": c.name, "description": c.description, "created_at": c.created_at.isoformat()}

@router.put("/{id}")
def update_category(id: int, data: CategoryCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Category).filter(Category.id == id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori tidak ditemukan")
    c.name = data.name
    c.description = data.description
    db.commit()
    db.refresh(c)
    return {"id": c.id, "name": c.name, "description": c.description, "created_at": c.created_at.isoformat()}

@router.delete("/{id}")
def delete_category(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    c = db.query(Category).filter(Category.id == id).first()
    if not c:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori tidak ditemukan")
    db.delete(c)
    db.commit()
    return {"message": "Kategori berhasil dihapus"}
