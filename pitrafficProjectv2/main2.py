import time
import requests
from pitrafficProjectv2.yolo_detect2 import get_vehicle_count
from gpio_control import set_led, cleanup_leds
from camera import capture_image

LANE_SEQUENCE = [1, 2, 3, 4]  # Define the sequence of lanes to process
CAMERA_INDEX = 0
BACKEND_URL = "http://192.168.100.100:8000/api/decision"  # Replace with your actual IP

try:
    # Ensure all lanes start at red
    for lane in LANE_SEQUENCE:
        set_led(lane, "red")

    current_index = 0  # Starting from first lane

    while True:
        current_lane = LANE_SEQUENCE[current_index]

        try:
            image_path = capture_image(CAMERA_INDEX, current_lane)
            count = get_vehicle_count(image_path)

            response = requests.post(BACKEND_URL, json={"lane": current_lane, "count": count})
            response.raise_for_status()
            duration = response.json()["green_duration"]

        except Exception as e:
            print(f"[ERROR] Communication or detection failed: {e}")
            duration = 10  # Default fallback duration

        if duration < 3:
            duration = 3  # Safety minimum

        # Phase 1: Current lane GREEN
        set_led(current_lane, "green")
        print(f"[INFO] Lane {current_lane} GREEN for {duration - 3}s")
        time.sleep(duration - 3)

        # Phase 2: Yellow phase for both current and next lanes
        set_led(current_lane, "yellow")

        # Determine next lane
        next_index = (current_index + 1) % len(LANE_SEQUENCE)
        next_lane = LANE_SEQUENCE[next_index]

        set_led(next_lane, "yellow")
        print(f"[INFO] Lane {current_lane} and Lane {next_lane} YELLOW for 3s")
        time.sleep(3)

        # Phase 3: Switch
        set_led(current_lane, "red")
        set_led(next_lane, "green")
        print(f"[INFO] Switching: Lane {current_lane} RED, Lane {next_lane} GREEN")

        # Update current lane
        current_index = next_index

except KeyboardInterrupt:
    print("[SYSTEM] Stopping system with Ctrl+C...")

finally:
    cleanup_leds()
    print("[SYSTEM] GPIO cleanup completed.")

