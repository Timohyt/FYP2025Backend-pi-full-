# utils/image_utils.py
import cv2

def img_to_bytes(img):
    success, encoded_image = cv2.imencode('.jpeg', img)
    if not success:
        raise ValueError("Failed to encode image")
    return encoded_image.tobytes()
