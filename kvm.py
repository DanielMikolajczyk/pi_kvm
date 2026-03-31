from pynput import keyboard, mouse
import time

# Tiny sample map: pynput keys to USB HID codes
# You will need to expand this!
KEYMAP = {
    'a': 4, 'b': 5, 'c': 6,
    keyboard.Key.enter: 40,
    keyboard.Key.space: 44,
    keyboard.Key.backspace: 42
}

# Open USB Gadgets
try:
    hid_kb = open('/dev/hidg0', 'wb')
    hid_mouse = open('/dev/hidg1', 'wb')
except FileNotFoundError:
    print("[ERROR] Run the USB Gadget setup script first!")
    exit()

def send_kb(hid_code):
    report = bytearray(8)
    report[2] = hid_code
    hid_kb.write(report)
    hid_kb.flush()

# --- KEYBOARD TRACKING ---
def on_press(key):
    try:
        # Standard character keys
        usb_code = KEYMAP.get(key.char, 0)
    except AttributeError:
        # Special keys (Enter, Space, etc.)
        usb_code = KEYMAP.get(key, 0)
    
    if usb_code != 0:
        send_kb(usb_code)

def on_release(key):
    send_kb(0) # Release all keys

# --- MOUSE TRACKING ---
last_x, last_y = None, None

def on_move(x, y):
    global last_x, last_y
    if last_x is not None and last_y is not None:
        dx = int(max(-127, min(127, x - last_x)))
        dy = int(max(-127, min(127, y - last_y)))
        
        if dx != 0 or dy != 0:
            report = bytearray([0, dx & 0xFF, dy & 0xFF, 0])
            hid_mouse.write(report)
            hid_mouse.flush()
            
    last_x, last_y = x, y

def on_click(x, y, button, pressed):
    btn_code = 1 if button == mouse.Button.left else 2 if button == mouse.Button.right else 0
    if pressed:
        hid_mouse.write(bytearray([btn_code, 0, 0, 0]))
    else:
        hid_mouse.write(bytearray([0, 0, 0, 0]))
    hid_mouse.flush()

# --- START THE LISTENERS ---
print("[INFO] Background KVM Running. Switch to VLC and start typing!")
print("[INFO] Press Ctrl+C in this terminal to stop.")

keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)

keyboard_listener.start()
mouse_listener.start()

keyboard_listener.join()
mouse_listener.join()