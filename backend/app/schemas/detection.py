from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class DetectionCreate(BaseModel):
    image_path: str
    detected_objects: List[Dict[str, Any]]

class DetectionResponse(BaseModel):
    id: int
    image_path: Optional[str]
    detected_objects: Optional[str]
    user_id: Optional[int]
    username: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
