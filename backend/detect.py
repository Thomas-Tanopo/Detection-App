import cv2
from ultralytics import YOLO

model = YOLO('yolov8n.pt')

cap = None
backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
for b in backends:
    for i in range(5):
        cap = cv2.VideoCapture(i, b)
        if cap.isOpened():
            print(f'Camera index {i} found (backend {b})')
            break
        cap.release()
    if cap and cap.isOpened():
        break

if not cap or not cap.isOpened():
    print('No camera found')
    exit()

cv2.namedWindow('Object Detection', cv2.WINDOW_NORMAL)
cv2.setWindowProperty('Object Detection', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)
    annotated = results[0].plot()

    cv2.imshow('Object Detection', annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
