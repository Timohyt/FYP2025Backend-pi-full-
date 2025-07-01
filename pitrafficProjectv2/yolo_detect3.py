#yolo_detect.py
import torch
import cv2
from pathlib import Path

model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt', force_reload=False)

SHOW_WINDOW = True
q_count = 0

def get_latest_image_for_lane(lane_number: int) -> str:
    snapshot_dir = Path("snapshots")
    images = sorted(snapshot_dir.glob(f"lane{lane_number}_*.jpeg"), reverse=True)
    if not images:
        print(f"[YOLO] No recent image found for lane {lane_number}.")
        return ""
    return str(images[0])

def get_vehicle_count(image_path: str) -> int:
    global q_count, SHOW_WINDOW

    if not image_path:
        return 0

    results = model(image_path)
    df = results.pandas().xyxy[0]

    vehicle_classes = ['car', 'truck', 'bus', 'motorbike']
    count = df[df['name'].isin(vehicle_classes)].shape[0]
    print(f"[YOLO] Detected {count} vehicles in {image_path}.")

    if SHOW_WINDOW:
        results.render()
        img = results.ims[0]
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow('YOLOv5 Detection', img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            q_count += 1
            if q_count >= 2:
                SHOW_WINDOW = False
                cv2.destroyAllWindows()
        elif key == ord('r'):
            SHOW_WINDOW = True
            q_count = 0

    return count
    