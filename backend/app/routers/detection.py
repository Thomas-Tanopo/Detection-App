import uuid, os, json
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.detection import Detection
from app.models.user import User
from app.auth_jwt import get_current_user
from app.services.detector import detect_objects, detect_from_frame

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
ALLOWED_MIME_PREFIXES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}

def _validate_image(file: UploadFile):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Format file tidak didukung: {ext}")
    content_type = file.content_type or ""
    if not any(content_type.startswith(m) for m in ALLOWED_MIME_PREFIXES):
        raise HTTPException(status_code=400, detail="File bukan gambar")
    return ext

@router.post("/upload")
async def upload_detect(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ext = _validate_image(file)
    filename = f"{uuid.uuid4()}{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)
    objects = detect_objects(filepath)
    det = Detection(image_path=filename, detected_objects=json.dumps(objects), user_id=user.id)
    db.add(det)
    db.commit()
    db.refresh(det)
    return {
        "detection_id": det.id,
        "image_url": f"/api/detection/image/{filename}",
        "detected_objects": objects,
        "created_at": det.created_at.isoformat()
    }

class FrameRequest(BaseModel):
    image: str

@router.post("/detect-frame")
def detect_frame(req: FrameRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        objects, annotated_b64, annotated_bytes = detect_from_frame(req.image)
        filename = f"{uuid.uuid4()}.jpg"
        filepath = os.path.join(settings.UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(annotated_bytes)
        det = Detection(image_path=filename, detected_objects=json.dumps(objects), user_id=user.id)
        db.add(det)
        db.commit()
        db.refresh(det)
        return {
            "detection_id": det.id,
            "image_url": f"/api/detection/image/{filename}",
            "detected_objects": objects,
            "created_at": det.created_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    dets = db.query(Detection).filter(Detection.user_id == user.id).order_by(Detection.created_at.desc()).all()
    result = []
    for d in dets:
        objects = json.loads(d.detected_objects) if d.detected_objects else []
        result.append({
            "id": d.id,
            "image_url": f"/api/detection/image/{d.image_path}" if d.image_path else None,
            "detected_objects": objects,
            "total_objects": len(objects),
            "created_at": d.created_at.isoformat()
        })
    return result

def _get_user_from_token_or_header(
    request: Request,
    token: str = Query(""),
    db: Session = Depends(get_db),
):
    auth_header = request.headers.get("Authorization", "")
    raw_token = ""
    if auth_header.startswith("Bearer "):
        raw_token = auth_header[7:]
    elif token:
        raw_token = token
    if not raw_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(raw_token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.get("/image/{filename}")
def get_detection_image(
    filename: str,
    user: User = Depends(_get_user_from_token_or_header),
):
    filepath = os.path.join(settings.UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Gambar tidak ditemukan")
    ext = os.path.splitext(filename)[1].lower()
    media_type = {
        ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".png": "image/png", ".webp": "image/webp",
        ".bmp": "image/bmp"
    }.get(ext, "application/octet-stream")
    return FileResponse(filepath, media_type=media_type)
