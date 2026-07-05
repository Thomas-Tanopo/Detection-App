from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import datetime, timedelta, date
from collections import Counter
import json
from app.database import get_db
from app.models.detection import Detection
from app.models.item import Item
from app.models.category import Category
from app.models.user import User
from app.routers.auth import get_current_user
from app.jinja_setup import templates

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    today = date.today()
    total_detections = db.query(Detection).count()
    total_items = db.query(Item).count()
    total_categories = db.query(Category).count()
    total_users = db.query(User).count()
    today_detections = db.query(Detection).filter(
        cast(Detection.created_at, Date) == today
    ).count()

    yesterday = today - timedelta(days=1)
    yesterday_detections = db.query(Detection).filter(
        cast(Detection.created_at, Date) == yesterday
    ).count()

    if yesterday_detections > 0:
        trend_pct = round(((today_detections - yesterday_detections) / yesterday_detections) * 100)
    else:
        trend_pct = 100 if today_detections > 0 else 0

    recent_detections = db.query(Detection).order_by(
        Detection.created_at.desc()
    ).limit(8).all()

    recent_list = []
    for d in recent_detections:
        objs = []
        if d.detected_objects:
            try:
                objs = json.loads(d.detected_objects)
            except (json.JSONDecodeError, TypeError):
                objs = []
        recent_list.append({
            "id": d.id,
            "image_path": d.image_path,
            "objects": objs[:3],
            "total_objects": len(objs),
            "created_at": d.created_at
        })

    detections_by_date = db.query(
        func.date(Detection.created_at).label("date"),
        func.count(Detection.id).label("count")
    ).group_by(
        func.date(Detection.created_at)
    ).order_by(
        func.date(Detection.created_at).desc()
    ).limit(14).all()

    chart_labels = []
    chart_data = []
    for i in range(13, -1, -1):
        d = today - timedelta(days=i)
        label = d.strftime("%d/%m")
        chart_labels.append(label)
        count = 0
        for rd in detections_by_date:
            if rd.date == d:
                count = rd.count
                break
        chart_data.append(count)

    all_objects = db.query(Detection.detected_objects).all()
    label_counter = Counter()
    for row in all_objects:
        if row[0]:
            try:
                objs = json.loads(row[0])
                for obj in objs:
                    label_counter[obj.get("label", "unknown")] += 1
            except (json.JSONDecodeError, TypeError):
                pass

    top_labels = label_counter.most_common(8)
    top_labels_names = [l[0] for l in top_labels]
    top_labels_counts = [l[1] for l in top_labels]

    return templates.TemplateResponse(request, "dashboard/index.html", {
        "user": user,
        "total_detections": total_detections,
        "total_items": total_items,
        "total_categories": total_categories,
        "total_users": total_users,
        "today_detections": today_detections,
        "trend_pct": trend_pct,
        "recent_list": recent_list,
        "chart_labels": chart_labels,
        "chart_data": chart_data,
        "top_labels_names": top_labels_names,
        "top_labels_counts": top_labels_counts
    })
