from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.item import Item
from app.models.category import Category
from app.auth_jwt import get_current_user
from app.models.user import User

router = APIRouter()

class ItemCreate(BaseModel):
    name: str
    description: str = ""
    category_id: int = 0

@router.get("")
def list_items(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    items = db.query(Item).order_by(Item.created_at.desc()).all()
    result = []
    for i in items:
        cat_name = i.category.name if i.category else None
        result.append({"id": i.id, "name": i.name, "description": i.description, "category_id": i.category_id, "category_name": cat_name, "created_at": i.created_at.isoformat()})
    return result

@router.post("")
def create_item(data: ItemCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.category_id:
        cat = db.query(Category).filter(Category.id == data.category_id).first()
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori tidak ditemukan")
    i = Item(name=data.name, description=data.description, category_id=data.category_id or None)
    db.add(i)
    db.commit()
    db.refresh(i)
    return {"id": i.id, "name": i.name, "description": i.description, "category_id": i.category_id, "created_at": i.created_at.isoformat()}

@router.get("/{id}")
def get_item(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    i = db.query(Item).filter(Item.id == id).first()
    if not i:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objek tidak ditemukan")
    return {"id": i.id, "name": i.name, "description": i.description, "category_id": i.category_id, "created_at": i.created_at.isoformat()}

@router.put("/{id}")
def update_item(id: int, data: ItemCreate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    i = db.query(Item).filter(Item.id == id).first()
    if not i:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objek tidak ditemukan")
    if data.category_id:
        cat = db.query(Category).filter(Category.id == data.category_id).first()
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategori tidak ditemukan")
    i.name = data.name
    i.description = data.description
    i.category_id = data.category_id or None
    db.commit()
    db.refresh(i)
    return {"id": i.id, "name": i.name, "description": i.description, "category_id": i.category_id, "created_at": i.created_at.isoformat()}

@router.delete("/{id}")
def delete_item(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    i = db.query(Item).filter(Item.id == id).first()
    if not i:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Objek tidak ditemukan")
    db.delete(i)
    db.commit()
    return {"message": "Objek berhasil dihapus"}
