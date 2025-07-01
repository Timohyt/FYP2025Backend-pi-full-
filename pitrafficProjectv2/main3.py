#main.py
import time
import requests
from gpio_control import set_led, cleanup_leds
from camera import capture_image
from yolo_detect import get_vehicle_count, get_latest_image_for_lane
from btrafficProjectv2.database import SessionLocal

LANE_SEQUENCE = [1, 2, 3, 4]
BACKEND_URL = "http://192.168.1.164:8000/api/decision"

try:
    for lane in LANE_SEQUENCE:
        set_led(lane, "red")

    current_index = 0
    initial_green_duration = 10

    first_lane = LANE_SEQUENCE[current_index]
    set_led(first_lane, "green")
    print(f"[SYSTEM] Initial lane {first_lane} GREEN for {initial_green_duration}s")
    time.sleep(initial_green_duration)

    while True:
        current_lane = LANE_SEQUENCE[current_index]
        next_index = (current_index + 1) % len(LANE_SEQUENCE)
        next_lane = LANE_SEQUENCE[next_index]

        # Phase 1: Current lane green
        set_led(current_lane, "green")
        print(f"[INFO] Lane {current_lane} GREEN")

        time.sleep(4)  # Countdown starts

        # Phase 2: t = 6s remaining ? capture for next lane
        #capture_image #(next_lane)

        with SessionLocal() as db:
         image_path = capture_image(next_lane, db)

        time.sleep(3)  # From t=6 to t=3

        # Phase 3: Yellow phase for both lanes
        set_led(current_lane, "yellow")
        set_led(next_lane, "yellow")
        print(f"[INFO] Lanes {current_lane} & {next_lane} YELLOW")
        time.sleep(3)

        # Analyze image & get green duration for next lane
        try:
            latest_image = get_latest_image_for_lane(next_lane)
            count = get_vehicle_count(latest_image)
            response = requests.post(BACKEND_URL, json={"lane": next_lane, "count": count})
            response.raise_for_status()
            green_duration = response.json().get("green_duration", 10)
        except Exception as e:
            print(f"[ERROR] {e}")
            green_duration = 10

        # Phase 4: Switch lanes
        set_led(current_lane, "red")
        set_led(next_lane, "green")
        print(f"[INFO] Switching to lane {next_lane} GREEN for {green_duration}s")
        time.sleep(green_duration)

        current_index = next_index

except KeyboardInterrupt:
    print("[SYSTEM] Exiting on Ctrl+C")
finally:
    cleanup_leds()
    print("[SYSTEM] GPIO cleanup done.")
