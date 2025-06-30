import cv2
import os
from datetime import datetime

SNAPSHOT_DIR = "snapshots"
os.makedirs(SNAPSHOT_DIR, exist_ok=True)

cap = cv2.VideoCapture(1)  # USB camera

def capture_image(lane_number: int) -> str:
    if not cap.isOpened():
        print("[CAMERA][ERROR] Camera not opened.")
        return ""
    
    # Flush buffer (of the USB camera): Read and discard a few frames
    for _ in range(5):
        cap.read()

    ret, frame = cap.read()
    if not ret:
        print("[CAMERA][ERROR] Cannot read frame.")
        return ""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"lane{lane_number}_{timestamp}.jpeg"
    filepath = os.path.join(SNAPSHOT_DIR, filename)

    cv2.imwrite(filepath, frame)
    print(f"[CAMERA] Captured image for lane {lane_number} at {timestamp}")
    return filepath

def show_live_feed():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[CAMERA] Frame not received.")
            break

        cv2.imshow("Live Feed", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[CAMERA] Live feed stopped.")
            break

    cap.release()
    cv2.destroyAllWindows()
