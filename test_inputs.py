from pynput import keyboard, mouse

# --- KEYBOARD EVENTS ---
def on_press(key):
    try:
        print(f"[KEYBOARD] Pressed: {key.char}")
    except AttributeError:
        # Handles special keys like Enter, Space, Shift, etc.
        print(f"[KEYBOARD] Special Key Pressed: {key}")

def on_release(key):
    print(f"[KEYBOARD] Released: {key}")
    # We need a way to kill the script! Pressing ESC will stop it.
    if key == keyboard.Key.esc:
        print("[INFO] Escape pressed. Exiting diagnostic tool...")
        # Returning False stops the listeners
        mouse_listener.stop()
        return False 

# --- MOUSE EVENTS ---
def on_move(x, y):
    # Warning: This will print A LOT of text very quickly
    print(f"[MOUSE] Moved to X: {x}, Y: {y}")

def on_click(x, y, button, pressed):
    action = "Clicked" if pressed else "Released"
    print(f"[MOUSE] {action} {button} at X: {x}, Y: {y}")

def on_scroll(x, y, dx, dy):
    direction = "Up" if dy > 0 else "Down"
    print(f"[MOUSE] Scrolled {direction} at X: {x}, Y: {y}")

# --- START THE LISTENERS ---
print("==================================================")
print("[INFO] Input Diagnostic Tool Running.")
print("[INFO] Click anywhere, move the mouse, or type.")
print("[INFO] Press the 'Esc' key to quit.")
print("==================================================")

# Set up the background listeners
keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll)

# Start them
keyboard_listener.start()
mouse_listener.start()

# Keep the script alive until ESC is pressed
keyboard_listener.join()
mouse_listener.join()