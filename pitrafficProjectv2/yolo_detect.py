# yolo_detect.py
import torch
import cv2
import os
from pathlib import Path
from logger import log
from btrafficProjectv2.crud import save_yolo_boxed_image
from utils.image_utils import img_to_bytes
from btrafficProjectv2.database import get_db

model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt', force_reload=False)

SHOW_WINDOW = True
q_count = 0
DETECTIONS_DIR = "detections"
os.makedirs(DETECTIONS_DIR, exist_ok=True)

def get_latest_image_for_lane(lane_number: int) -> str:
    snapshot_dir = Path("snapshots")
    images = sorted(snapshot_dir.glob(f"lane{lane_number}_*.jpeg"), reverse=True)
    if not images:
        log(f"[YOLO] No recent image found for lane {lane_number}.")
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
    log(f"[YOLO] Detected {count} vehicles in {image_path}.")

    for _, row in df.iterrows():
        if row['name'] in vehicle_classes:
            log(f"  - {row['name']} @ {row['confidence']:.2f}")

    # Save image with boxes
    results.render()
    boxed_img = results.ims[0]
    boxed_img_bgr = cv2.cvtColor(boxed_img, cv2.COLOR_RGB2BGR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lane_number = int(Path(image_path).stem.split('_')[0].replace("lane", ""))
    boxed_filename = f"boxed_lane{lane_number}_{timestamp}.jpeg"
    boxed_path = os.path.join(DETECTIONS_DIR, boxed_filename)

    cv2.imwrite(boxed_path, boxed_img_bgr)
    log(f"[YOLO] Saved boxed image: {boxed_filename}")

    # Store in DB
    image_bytes = img_to_bytes(boxed_img_bgr)
    with next(get_db()) as db:
        save_yolo_boxed_image(db, lane=lane_number, filename=boxed_filename, image_data=image_bytes)

    # Show if enabled
    if SHOW_WINDOW:
        cv2.imshow("YOLOv5 Detection", boxed_img_bgr)
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
