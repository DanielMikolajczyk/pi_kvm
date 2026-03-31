import tkinter as tk

# Expand this for all your keys
KEYMAP = {
    'a': 4, 'A': 4,
    'b': 5, 'B': 5,
    'Return': 40,
    'space': 44,
    'BackSpace': 42
}

class ResilientKVM:
    def __init__(self, root):
        self.root = root
        self.root.title("KVM Capture (Click here to type)")
        self.root.geometry("400x300")
        self.root.configure(bg='black')
        
        # Try to make it slightly transparent (Wayland usually allows this if it's not fullscreen)
        try:
            self.root.attributes('-alpha', 0.8)
        except:
            pass

        # Open USB endpoints
        try:
            self.hid_kb = open('/dev/hidg0', 'wb')
            self.hid_mouse = open('/dev/hidg1', 'wb')
        except FileNotFoundError:
            print("[ERROR] USB Gadget files not found!")
            exit(1)

        self.last_x, self.last_y = None, None
        self.mouse_btns = 0

        # Bind events
        self.root.bind('<KeyPress>', self.on_press)
        self.root.bind('<KeyRelease>', self.on_release)
        self.root.bind('<Motion>', self.on_move)
        self.root.bind('<Button>', self.on_click)
        self.root.bind('<ButtonRelease>', self.on_release_click)

        lbl = tk.Label(root, text="KVM CAPTURE ACTIVE\n\nClick this window to capture.\nMove mouse or type.\nPress ESC to close.", fg="green", bg="black")
        lbl.pack(expand=True)

    def send_kb(self, hid_code):
        report = bytearray(8)
        report[2] = hid_code
        try:
            print(f"[DEBUG KB] Sending hex: {report.hex()} (HID Code: {hid_code})")
            self.hid_kb.write(report)
            self.hid_kb.flush()
        except BrokenPipeError:
            print("[WARNING] KB Pipe Broken: Target laptop rejected the data.")
        except BlockingIOError:
            pass

    def send_mouse(self, dx, dy):
        dx = max(-127, min(127, dx))
        dy = max(-127, min(127, dy))
        report = bytearray([self.mouse_btns, dx & 0xFF, dy & 0xFF, 0])
        try:
            print(f"[DEBUG MOUSE] Sending hex: {report.hex()} (dx:{dx}, dy:{dy}, btn:{self.mouse_btns})")
            self.hid_mouse.write(report)
            self.hid_mouse.flush()
        except BrokenPipeError:
            print("[WARNING] MOUSE Pipe Broken: Target laptop rejected the data.")
        except BlockingIOError:
            pass

    def on_press(self, event):
        if event.keysym == 'Escape':
            print("[INFO] Exiting KVM...")
            self.root.destroy()
            return
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
        self.send_mouse(0, 0)

    def on_release_click(self, event):
        self.mouse_btns = 0
        self.send_mouse(0, 0)

if __name__ == "__main__":
    root = tk.Tk()
    app = ResilientKVM(root)
    root.mainloop()