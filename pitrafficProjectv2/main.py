import time
import requests
import base64
import os
import sys
from gpio_control import set_led, cleanup_leds
from camera import capture_image
from yolo_detect import get_vehicle_count, get_latest_image_for_lane
from btrafficProjectv2.database import SessionLocal

# ------------------ Configuration ------------------

LANE_SEQUENCE = [1, 2, 3, 4]

# Get backend URL from environment variable
BACKEND_HOST = os.getenv("BACKEND_HOST", "192.168.1.164")
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
BACKEND_BASE_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/api"

URLS = {
    "decision": f"{BACKEND_BASE_URL}/decision",
    "status": f"{BACKEND_BASE_URL}/status",
    "monitoring": f"{BACKEND_BASE_URL}/monitoring",
    "manual": f"{BACKEND_BASE_URL}/manual",
    "analytics": f"{BACKEND_BASE_URL}/analytics",
    "reports": f"{BACKEND_BASE_URL}/reports"
}

print(f"🔗 Backend API: {BACKEND_BASE_URL}")

# Test backend connectivity
def test_backend_connection():
    try:
        response = requests.get(f"{BACKEND_BASE_URL}/status", timeout=5)
        print(f"✅ Backend connection successful")
        return True
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False

# ------------------ Initial Setup ------------------

try:
    # Test backend connectivity before starting
    if not test_backend_connection():
        print("⚠️  Warning: Backend not accessible, but continuing with local operation")
    
    for lane in LANE_SEQUENCE:
        set_led(lane, "red")

    current_index = 0
    initial_green_duration = 10

    first_lane = LANE_SEQUENCE[current_index]
    set_led(first_lane, "green")
    print(f"[SYSTEM] Initial lane {first_lane} GREEN for {initial_green_duration}s")
    time.sleep(initial_green_duration)

    # ------------------ Main Loop ------------------

    while True:
        current_lane = LANE_SEQUENCE[current_index]
        next_index = (current_index + 1) % len(LANE_SEQUENCE)
        next_lane = LANE_SEQUENCE[next_index]

        # Phase 1: Current lane green
        set_led(current_lane, "green")
        print(f"[INFO] Lane {current_lane} GREEN")
        time.sleep(4)

        # Phase 2: Capture image for next lane
        try:
            with SessionLocal() as db:
                image_path = capture_image(next_lane, db)
        except Exception as e:
            print(f"[ERROR] Image capture failed: {e}")
            image_path = None

        time.sleep(3)

        # Phase 3: Both lanes yellow
        set_led(current_lane, "yellow")
        set_led(next_lane, "yellow")
        print(f"[INFO] Lanes {current_lane} & {next_lane} YELLOW")
        time.sleep(3)

        # Phase 4: Analyze image and get decision
        green_duration = 10  # Default fallback
        
        if image_path:
            try:
                latest_image = get_latest_image_for_lane(next_lane)
                count = get_vehicle_count(latest_image)

                # Encode image to base64
                with open(latest_image, "rb") as img_file:
                    encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

                # Send decision request with image
                payload = {
                    "lane": next_lane,
                    "count": count,
                    "captured_image": encoded_image # You can also add boxed_image if needed
                }

                response = requests.post(URLS["decision"], json=payload, timeout=10)
                response.raise_for_status()

                green_duration = response.json().get("green_duration", 10)
                print(f"[INFO] Backend decided {green_duration}s GREEN for lane {next_lane} (vehicles: {count})")

            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Backend request failed: {e}")
                print(f"[INFO] Using local fallback decision: {green_duration}s")
            except Exception as e:
                print(f"[ERROR] Decision processing failed: {e}")
                print(f"[INFO] Using default duration: {green_duration}s")
        else:
            print(f"[WARNING] No image available, using default duration: {green_duration}s")

        # Phase 5: Switch lane
        set_led(current_lane, "red")
        set_led(next_lane, "green")
        print(f"[INFO] Switching to lane {next_lane} GREEN for {green_duration}s")
        time.sleep(green_duration)

        current_index = next_index

# ------------------ Exit Gracefully ------------------

except KeyboardInterrupt:
    print("[SYSTEM] Exiting on Ctrl+C")

finally:
    cleanup_leds()
    print("[SYSTEM] GPIO cleanup done.")
