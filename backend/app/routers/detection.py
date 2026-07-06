import uuid, os, json
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.detection import Detection
from app.models.user import User
from app.auth_jwt import get_current_user
from app.services.detector import detect_objects, detect_from_frame

router = APIRouter()

@router.post("/upload")
async def upload_detect(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[1] or ".jpg"
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
        "image_url": f"/uploads/{filename}",
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
            "image_url": f"/uploads/{filename}",
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
            "image_url": f"/uploads/{d.image_path}" if d.image_path else None,
            "detected_objects": objects,
            "total_objects": len(objects),
            "created_at": d.created_at.isoformat()
        })
    return result
