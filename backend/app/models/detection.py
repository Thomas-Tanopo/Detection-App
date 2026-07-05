from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Detection(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(255))
    detected_objects = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="detections")

class DetectionItem(Base):
    __tablename__ = "detection_items"

    id = Column(Integer, primary_key=True, index=True)
    detection_id = Column(Integer, ForeignKey("detections.id", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("items.id"))
    label = Column(String(100))
    confidence = Column(Float)
    quantity = Column(Integer, default=1)

    detection = relationship("Detection", backref="detection_items")
    item = relationship("Item", backref="detection_items")
