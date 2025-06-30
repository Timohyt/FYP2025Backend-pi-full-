import torch
import cv2
from pathlib import Path

# Load the YOLOv5s model from local weights file
model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt', force_reload=False)


SHOW_WINDOW = True  # Set to False to disable window display
q_count = 0

def get_vehicle_count(image_path):

    global q_count, SHOW_WINDOW
    
    results = model(image_path)
    df = results.pandas().xyxy[0]

    #Filter for relevant vehicle classes
    vehicle_classes = ['car', 'truck', 'bus', 'motorbike']
    count = df[df['name'].isin(vehicle_classes)].shape[0]
    print(f"[YOLO] Detected {count} vehicles in {image_path}.")

    ##added snippet for detection window visualization display
    if SHOW_WINDOW:
        #Render results (draw boxes on image)
        results.render()

        #Convert rendered images from RGB to BGR for OpenCV display
        img = results.ims[0]  # Get the first image
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        #Display the image with bounding boxes
        cv2.imshow('YOLOv5 Detection', img)

        # Wait for a key press to close the window
        key = cv2.waitKey(1) & 0xFF # <-- 1ms


        if key == ord('q'):
            q_count += 1
            print(f"[INFO] Pressed 'q' ({q_count} time(s))")
            
            if q_count >= 2:
                SHOW_WINDOW = False
                print("[INFO] Permanently disabled YOLO window display.")
                cv2.destroyAllWindow()

        elif key == ord('r'):
            SHOW_WINDOW = True
            q_count = 0
            print("[INFO] Re-enabled YOLO window display.")  

    #####
    
    return count
