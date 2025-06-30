import RPi.GPIO as GPIO
import time

# Pin mapping for each LED by lane
# Format: { lane_number: {color: GPIO_pin_number} }
LANE_LED_PINS = {
    1: {"red": 2, "yellow": 3, "green": 4},
    2: {"red": 17, "yellow": 27, "green": 22},
    3: {"red": 10, "yellow": 9, "green": 11},
    4: {"red": 5, "yellow": 6, "green": 13},
}

# Initialize GPIO pins once
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup all pins as OUTPUT
for lane_pins in LANE_LED_PINS.values():
    for pin in lane_pins.values():
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.LOW)  # Turn off all LEDs initially


def set_led(lane: int, color: str):
    if lane not in LANE_LED_PINS or color not in LANE_LED_PINS[lane]:
        print(f"[LED][ERROR] Invalid lane ({lane}) or color ({color})")
        return

    # Turn off all LEDs for this lane first
    for c in LANE_LED_PINS[lane]:
        GPIO.output(LANE_LED_PINS[lane][c], GPIO.LOW)

    # Turn on only the requested color LED
    GPIO.output(LANE_LED_PINS[lane][color], GPIO.HIGH)

    print(f"[LED] Lane {lane} -> {color.upper()} light")

def cleanup_leds():
    GPIO.cleanup()