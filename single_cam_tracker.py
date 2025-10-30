from ultralytics import YOLO
import cv2
import serial
import time
from sort import Sort
import numpy as np
# --- serial ---
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
    print("✅ Połączono z /dev/ttyACM0")
except Exception as e:
    print("❌ Nie udało się otworzyć portu:", e)
    ser = None

# --- YOLO ---
model = YOLO('yolo11n.pt')
print("✅ Model przeniesiony na CUDA")
tracker = Sort(max_age=5, min_hits=1, iou_threshold=0.3)
RESET_INTERVAL = 5.0  # co ile sekund resetować
last_reset_time = time.time()
now = time.time()
if now - last_reset_time > RESET_INTERVAL:
    tracker = Sort(max_age=5, min_hits=1, iou_threshold=0.3)
    last_reset_time = now
    print("🔄 Reset tracker IDs")
# --- kamera ---
VIDEO_SOURCE = '/dev/video4'
cap = cv2.VideoCapture(VIDEO_SOURCE)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FPS, 30)

# --- wygładzanie ---
smooth_x, smooth_y = 320, 180  # start w centrum
alpha = 0.2
last_send_time = 0
SEND_INTERVAL = 0.05  # minimalny interwał wysyłki
last_sent_coords = (0, 0)
MIN_MOVE = 5  # minimalna zmiana pozycji, żeby wysyłać

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame,0)
    results = model(frame, device='cuda', classes=[0])  # tylko ludzie

    person_center = None
    max_area = 0
    detections =[]
    for r in results:
        if r.boxes is not None:
            for box, conf in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.conf.cpu().numpy()):
                if conf < 0.7:  # filtr: tylko jeśli pewność >50%
                    continue
                x1, y1, x2, y2 = box
                area = (x2 - x1) * (y2 - y1)

                height_px = y2 - y1
                ref_height_px = 300  # np. przy 1 m odległości
                distance_m = (1.0 * ref_height_px) / max(height_px, 1)
                frame_h, frame_w = frame.shape[:2]
                # Ucięcie na krawędzi
                detections.append([x1, y1, x2, y2, conf])

                if x1 < 50 or x2 > (frame_w - 50):
                    distance_valid = False
                else:
                    distance_valid = True

                # Wygładzanie odległości
                if distance_valid:
                    distance_m = 0.8 * distance_m + 0.2 * (1.0 * ref_height_px / height_px)

                # Wysyłanie tylko jeśli wiarygodne
                if ser and distance_valid:
                    msg = f"Wysokosc {smooth_x},{smooth_y},{distance_m:.2f}"
                    cos = cv2.putText(frame, f'ID: {str(msg)}', (int(x1 + 400), int(y1-100)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2,cv2.LINE_AA)
                    cv2.imshow('YOLO People Tracker', cos)

                if area > max_area:
                    max_area = area
                    cx = int((x1 + x2) / 2)
                    cy = int(y1 - (y1 / 10)) # podnosimy kropkę
                    person_center = (cx, cy)
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    if len(detections) > 0:
        tracked_objects = tracker.update(np.array(detections))
    else:
        tracked_objects = []

    for x1, y1, x2, y2, obj_id in tracked_objects:
        x1, y1, x2, y2, obj_id = int(x1), int(y1), int(x2), int(y2), int(obj_id)
        # cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv2.putText(frame, f'ID: {obj_id}', (x1 + 400, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,255,0), 2)
    
    if person_center is not None:
        # --- wygładzanie ---
        smooth_x = int(smooth_x * (1 - alpha) + person_center[0] * alpha)
        smooth_y = int(smooth_y * (1 - alpha) + person_center[1] * alpha)

        # --- wysyłanie tylko jeśli ruch > MIN_MOVE i po SEND_INTERVAL ---
        dx = abs(smooth_x - last_sent_coords[0])
        dy = abs(smooth_y - last_sent_coords[1])
        now = time.time()
        if ser and ((dx > MIN_MOVE or dy > MIN_MOVE) and (now - last_send_time >= SEND_INTERVAL)):
            msg = f"{smooth_x},{smooth_y}\n"
            try:
                ser.write(msg.encode())
            except:
                pass
            last_send_time = now
            last_sent_coords = (smooth_x, smooth_y)

        # rysowanie kropki
        cv2.circle(frame, (smooth_x, smooth_y), 5, (0, 0, 255), -1)
        # cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.imshow('YOLO People Tracker', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
if ser:
    ser.close()
