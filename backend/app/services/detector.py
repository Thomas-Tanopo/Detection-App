import cv2
import os
import base64
import numpy as np

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None

_model = None

def get_model():
    global _model
    if _model is None:
        model_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "yolov8n.pt"
        )
        if os.path.exists(model_path):
            _model = YOLO(model_path)
    return _model

def detect_objects(image_path: str):
    model = get_model()
    if model is None:
        return []

    results = model(image_path)
    detected = []

    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            detected.append({
                "label": r.names[int(box.cls[0])],
                "confidence": round(float(box.conf[0]), 4),
                "bbox": [round(x, 2) for x in box.xyxy[0].tolist()]
            })

    return detected

def detect_from_frame(image_data: str):
    model = get_model()
    if model is None:
        return [], None, None

    if "," in image_data:
        image_data = image_data.split(",")[1]

    img_bytes = base64.b64decode(image_data)
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = model(frame)
    detected = []

    for r in results:
        if r.boxes is None:
            continue
        annotated = r.plot()
        for box in r.boxes:
            detected.append({
                "label": r.names[int(box.cls[0])],
                "confidence": round(float(box.conf[0]), 4),
                "bbox": [round(x, 2) for x in box.xyxy[0].tolist()]
            })

    _, buffer = cv2.imencode(".jpg", annotated)
    annotated_bytes = buffer.tobytes()
    annotated_base64 = base64.b64encode(annotated_bytes).decode("utf-8")

    return detected, f"data:image/jpeg;base64,{annotated_base64}", annotated_bytes
