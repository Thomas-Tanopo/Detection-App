from fastapi import APIRouter, Request, Depends, UploadFile, File
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
import os
import uuid
import json
from app.database import get_db
from app.models.detection import Detection
from app.routers.auth import get_current_user
from app.config import settings
from app.services.detector import detect_objects, detect_from_frame
from app.jinja_setup import templates

router = APIRouter(prefix="/detection", tags=["detection"])

@router.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse(request, "detection/upload.html", {
        "user": user
    })

@router.get("/camera", response_class=HTMLResponse)
async def camera_page(
    request: Request,
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    return templates.TemplateResponse(request, "detection/camera.html", {
        "user": user
    })

@router.post("/upload")
async def detect_upload(
    request: Request,
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)

    ext = os.path.splitext(image.filename)[1] or ".jpg"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    content = await image.read()
    with open(filepath, "wb") as f:
        f.write(content)

    detected_objects = detect_objects(filepath)

    detection = Detection(
        image_path=f"static/uploads/{filename}",
        detected_objects=json.dumps(detected_objects),
        user_id=user.id
    )
    db.add(detection)
    db.commit()
    db.refresh(detection)

    return templates.TemplateResponse(request, "detection/result.html", {
        "user": user,
        "detection": detection,
        "detected_objects": detected_objects,
        "image_url": f"/static/uploads/{filename}"
    })

@router.post("/detect-frame")
async def detect_frame(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)

    data = await request.json()
    image_data = data.get("image", "")

    detected_objects, _, annotated_bytes = detect_from_frame(image_data)

    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(annotated_bytes)

    detection = Detection(
        image_path=f"static/uploads/{filename}",
        detected_objects=json.dumps(detected_objects),
        user_id=user.id
    )
    db.add(detection)
    db.commit()
    db.refresh(detection)

    return JSONResponse({
        "detection_id": detection.id,
        "detected_objects": detected_objects,
        "image_url": f"/static/uploads/{filename}"
    })

@router.get("/history", response_class=HTMLResponse)
async def history(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user)
):
    if not user:
        return RedirectResponse(url="/auth/login", status_code=302)
    detections = db.query(Detection).filter(
        Detection.user_id == user.id
    ).order_by(Detection.created_at.desc()).all()
    return templates.TemplateResponse(request, "detection/history.html", {
        "user": user,
        "detections": detections
    })
