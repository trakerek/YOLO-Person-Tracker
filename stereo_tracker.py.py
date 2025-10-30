from ultralytics import YOLO
import cv2
import serial
import time
from sort import *  # import SORT
import math

# --- serial ---
try:
    ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
    print("✅ Połączono z /dev/ttyACM0")
except Exception as e:
    print("❌ Nie udało się otworzyć portu:", e)
    ser = None

#----------------CONFIG
FRAME_WIDTH = 3840 #2560   / 3840
FRAME_HEIGHT = 1080 #729    / 1080


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
cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FPS, 30)

# --- wygładzanie ---
smooth_x, smooth_y = 1920, 540  # start w centrum obu "kamer"
alpha = 0.2
last_send_time = 0
SEND_INTERVAL = 0.05
last_sent_coords = (0, 0)
MIN_MOVE = 5
height = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 0)
    frame1 = frame[:, :FRAME_WIDTH // 2]
    frame2 = frame[:, FRAME_WIDTH // 2:]
    frame2_resized = cv2.resize(frame2, (frame1.shape[1], frame1.shape[0]))
    combined = cv2.addWeighted(frame1, 0.5, frame2_resized, 0.5, 0)

    # Środki kamer w combined
# frame1 i frame2_resized mają tę samą szerokość
    cam1_center = (frame1.shape[1] // 2, frame1.shape[0] // 2)  # środek frame1
    cam2_center = (frame2_resized.shape[1] // 2, frame2_resized.shape[0] // 2)  # środek frame2 w combined
    # YOLO na combined
    results1 = model(frame1, device='cuda', classes=[0])
    results2 = model(frame2, device='cuda', classes=[0])

    person_centers = []
    for r in results1:
        if r.boxes is not None:
            for box, conf in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.conf.cpu().numpy()):
                if conf < 0.5:
                    continue

                x1, y1, x2, y2 = box
                cx = int((x1 + x2) / 2)
                cyy = int((y1 + y2) / 2)
                cy = int(y1 - (y1 / 5))
                person_centers.append((cx, cy))
                
                # Bounding box i opis
                cv2.rectangle(combined, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(combined, f"Person: {str(round(conf,2))}", (int(x1), int(y1)),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)

                # Linia od środków kamer do osoby
                # cv2.line(combined, cam1_center, (int(FRAME_WIDTH / 4), int(FRAME_HEIGHT)), (0,0,255), 2)   # czerwona z lewej kamery
                cv2.line(combined, (cx,cyy), (FRAME_WIDTH // 4, FRAME_HEIGHT), (0,255,0), 2)   # zielona z prawej kamery

                # cv2.line(combined, cam1_center, cam2_center, (255,0,0), 1) # niebieska między kamerami

    for r in results2:
        if r.boxes is not None:
            for box, conf in zip(r.boxes.xyxy.cpu().numpy(), r.boxes.conf.cpu().numpy()):
                if conf < 0.5:
                    continue

                x1, y1, x2, y2 = box
                cx = int((x1 + x2) / 2)
                cyy = int((y1 + y2) / 2)
                cy = int(y1 - (y1 / 5))
                person_centers.append((cx, cy))

                # Bounding box i opis
                cv2.rectangle(combined, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(combined, f"Person: {str(round(conf,2))}", (int(x1), int(y1)),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)

                # Linia od środków kamer do osoby
                # cv2.line(combined, cam1_center, (int(FRAME_WIDTH / 4), int(FRAME_HEIGHT)), (0,0,255), 2)   # czerwona z lewej kamery
                cv2.line(combined, (cx,cyy), (FRAME_WIDTH // 4, FRAME_HEIGHT), (0,255,0), 2)   # zielona z prawej kamery
                # cv2.line(combined, cam1_center, cam2_center, (255,0,0), 1) # niebieska między kamerami

    # Wyliczanie średniego środka wszystkich osób dla sterowania
    # baseline w metrach
    B = 0.05  # 5 cm

        # ogniskowa w pikselach (przykład, możesz zmienić wg FOV kamery)
    f = 500
    # Wyliczanie średniego środka wszystkich osób dla sterowania i odległości
    if person_centers:
    # Zakładamy, że osoba wykryta w obu kamerach ma podobny indeks
        if len(results1[0].boxes) > 0 and len(results2[0].boxes) > 0:
            box1 = results1[0].boxes.xyxy.cpu().numpy()[0]  # lewa kamera
            box2 = results2[0].boxes.xyxy.cpu().numpy()[0]  # prawa kamera

            cx1 = int((box1[0] + box1[2]) / 2)
            cx2 = int((box2[0] + box2[2]) / 2)

            disparity = cx1 - cx2
            if disparity != 0:
                Z = (f * B) / disparity  # odległość w metrach
            else:
                Z = -1  # nie można policzyć

            # Środek kamery w obrazie
            cam_center = (frame1.shape[1]//2, frame1.shape[0]//2)
            person_center = (cx1, int((box1[1] + box1[3]) / 2))

            # Rysowanie odległości na obrazie
            if Z > 0:
                cv2.putText(combined, f"Distance: {Z:.2f} m", (FRAME_WIDTH//4, FRAME_HEIGHT//8),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255,0,0), 2, cv2.LINE_AA)
        else:
            # Jeśli nie wykryto osoby w obu kamerach, pomijamy obliczenia
            Z = -1
            person_center = (smooth_x, smooth_y)

        avg_x = int(sum([c[0] for c in person_centers]) / len(person_centers))
        avg_y = int(sum([c[1] for c in person_centers]) / len(person_centers))
        person_center = (avg_x, avg_y)

        smooth_x = int(smooth_x * (1 - alpha) + person_center[0] * alpha)
        smooth_y = int(smooth_y * (1 - alpha) + person_center[1] * alpha)

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

        # Kropka w wygładzonym środku
        cv2.circle(combined, (smooth_x, smooth_y), 5, (0, 0, 255), -1)

    cv2.imshow('YOLO People Tracker', combined)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cap.release()
cv2.destroyAllWindows()
if ser:
    ser.close()
