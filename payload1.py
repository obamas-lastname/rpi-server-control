import time
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

def simulate_payload():
    # Wait a moment to allow the OS to recognize the device
    time.sleep(1)

    # Create a keyboard object
    keyboard = Keyboard(usb_hid.devices)
    keyboard_layout = KeyboardLayoutUS(keyboard)

    # Simulate opening Notepad (Windows: Win+R, then "notepad", then Enter)
    keyboard.send(Keycode.WINDOWS, Keycode.R)
    time.sleep(0.5)
    keyboard_layout.write("notepad\n")
    time.sleep(1)  # Wait for Notepad to open

    # Simulate typing the message
    keyboard_layout.write("Payload1 would have been executed")

    # Release the keyboard
    keyboard.release_all()

# Start the simulated payload
simulate_payload()
