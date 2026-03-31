import tkinter as tk

# Tiny sample map: Expand this for all keys!
KEYMAP = {
    'a': 4, 'A': 4,
    'b': 5, 'B': 5,
    'c': 6, 'C': 6,
    'd': 7, 'D': 7,
    'e': 8, 'E': 8,
    'f': 9, 'F': 9,
    'g': 10, 'G': 10,
    'h': 11, 'H': 11,
    'i': 12, 'I': 12,
    'j': 13, 'J': 13,
    'k': 14, 'K': 14,
    'l': 15, 'L': 15,
    'm': 16, 'M': 16,
    'n': 17, 'N': 17,
    'o': 18, 'O': 18,
    'u': 19, 'U': 19,
    'p': 20, 'P': 20,
    'r': 21, 'R': 21,
    's': 22, 'S': 22,
    't': 23, 'T': 23,
    'u': 24, 'U': 24,
    'w': 25, 'W': 25,
    'x': 26, 'X': 26,
    'y': 27, 'Y': 27,
    'z': 28, 'Z': 28,
    'Return': 40,
    'space': 44,
    'BackSpace': 42
}

class StealthKVM:
    def __init__(self, root):
        self.root = root
        
        # 1. Hardcode the exact 1080p resolution and force it to the top-left corner (0,0)
        self.root.geometry("1920x1080+0+0")
        
        # 2. Linux trick: Make it a "splash" screen. 
        # This removes borders but keeps keyboard focus (unlike overrideredirect)
        self.root.attributes('-type', 'splash')
        
        # 3. Keep it on top of VLC
        self.root.attributes("-topmost", True)
        self.root.configure(bg='black')
        
        # 4. Force the OS to draw the 1080p canvas BEFORE applying transparency
        self.root.update_idletasks()
        self.root.focus_force()
        
        # 5. Apply Transparency
        self.root.wait_visibility(self.root)
        self.root.attributes("-alpha", 0.15) 
        
        # Open USB endpoints
        try:
            self.hid_kb = open('/dev/hidg0', 'wb')
            self.hid_mouse = open('/dev/hidg1', 'wb')
        except FileNotFoundError:
            print("[ERROR] USB Gadget files not found!")
            exit(1)

        self.last_x = None
        self.last_y = None
        self.mouse_btns = 0

        # Bind events
        self.root.bind('<KeyPress>', self.on_press)
        self.root.bind('<KeyRelease>', self.on_release)
        self.root.bind('<Motion>', self.on_move)
        self.root.bind('<Button>', self.on_click)
        self.root.bind('<ButtonRelease>', self.on_release_click)
        
        # EXPLICIT KILL SWITCHES
        self.root.bind('<Escape>', self.emergency_exit)
        self.root.bind('<Button-2>', self.emergency_exit) # Middle Mouse Button

    def emergency_exit(self, event=None):
        print("[INFO] Exiting Stealth KVM...")
        self.root.destroy()

    def send_kb(self, hid_code):
        report = bytearray(8)
        report[2] = hid_code
        try:
            self.hid_kb.write(report)
            self.hid_kb.flush()
        except (BrokenPipeError, BlockingIOError):
            pass 

    def send_mouse(self, dx, dy):
        dx = max(-127, min(127, dx))
        dy = max(-127, min(127, dy))
        report = bytearray([self.mouse_btns, dx & 0xFF, dy & 0xFF, 0])
        try:
            self.hid_mouse.write(report)
            self.hid_mouse.flush()
        except (BrokenPipeError, BlockingIOError):
            pass 

    def on_press(self, event):
        usb_code = KEYMAP.get(event.keysym, 0)
        if usb_code != 0:
            self.send_kb(usb_code)

    def on_release(self, event):
        if event.keysym in KEYMAP:
            self.send_kb(0)

    def on_move(self, event):
        if self.last_x is not None and self.last_y is not None:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            if dx != 0 or dy != 0:
                self.send_mouse(dx, dy)
        self.last_x, self.last_y = event.x, event.y

    def on_click(self, event):
        if event.num == 1: self.mouse_btns = 1
        elif event.num == 3: self.mouse_btns = 2
        
        # Don't send mouse click to target if it's the middle click (our exit button)
        if event.num != 2: 
            self.send_mouse(0, 0)

    def on_release_click(self, event):
        self.mouse_btns = 0
        if event.num != 2:
            self.send_mouse(0, 0)

if __name__ == "__main__":
    print("[INFO] Stealth KVM Starting...")
    print("[INFO] Press 'ESC' or click the MIDDLE MOUSE BUTTON to kill the KVM overlay.")
    root = tk.Tk()
    app = StealthKVM(root)
    root.mainloop()