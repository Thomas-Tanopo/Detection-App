import json
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.detection import Detection
from app.models.user import User
from app.models.item import Item
from app.models.category import Category
from app.auth_jwt import get_current_user

router = APIRouter()

@router.get("/stats")
def stats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    today_count = db.query(Detection).filter(func.date(Detection.created_at) == today).count()
    total_detections = db.query(Detection).count()
    total_items = db.query(Item).count()
    total_categories = db.query(Category).count()
    total_users = db.query(User).count()
    yesterday = today - timedelta(days=1)
    yesterday_count = db.query(Detection).filter(func.date(Detection.created_at) == yesterday).count()
    trend_pct = 0
    if yesterday_count > 0:
        trend_pct = round((today_count - yesterday_count) / yesterday_count * 100)
    return {
        "today_detections": today_count,
        "total_detections": total_detections,
        "total_items": total_items,
        "total_categories": total_categories,
        "total_users": total_users,
        "trend_pct": trend_pct
    }

@router.get("/trend")
def trend(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    labels = []
    data = []
    for i in range(13, -1, -1):
        day = datetime.utcnow().date() - timedelta(days=i)
        count = db.query(Detection).filter(func.date(Detection.created_at) == day).count()
        labels.append(day.strftime("%d %b"))
        data.append(count)
    return {"labels": labels, "data": data}

@router.get("/top-labels")
def top_labels(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dets = db.query(Detection).order_by(Detection.created_at.desc()).limit(100).all()
    label_count = {}
    for d in dets:
        if d.detected_objects:
            objects = json.loads(d.detected_objects)
            for obj in objects:
                label = obj.get("label", "Unknown")
                label_count[label] = label_count.get(label, 0) + 1
    sorted_labels = sorted(label_count.items(), key=lambda x: x[1], reverse=True)[:8]
    return {"names": [l[0] for l in sorted_labels], "counts": [l[1] for l in sorted_labels]}

@router.get("/recent")
def recent(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dets = db.query(Detection).order_by(Detection.created_at.desc()).limit(10).all()
    result = []
    for d in dets:
        objects = json.loads(d.detected_objects) if d.detected_objects else []
        result.append({
            "id": d.id,
            "image_url": f"/uploads/{d.image_path}" if d.image_path else None,
            "objects": objects,
            "total_objects": len(objects),
            "created_at": d.created_at.isoformat()
        })
    return result
