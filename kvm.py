import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

# Your exact KEYMAP (perfectly matches GTK key names!)
KEYMAP = {
    'a': 4, 'A': 4, 'b': 5, 'B': 5, 'c': 6, 'C': 6, 'd': 7, 'D': 7,
    'e': 8, 'E': 8, 'f': 9, 'F': 9, 'g': 10, 'G': 10, 'h': 11, 'H': 11,
    'i': 12, 'I': 12, 'j': 13, 'J': 13, 'k': 14, 'K': 14, 'l': 15, 'L': 15,
    'm': 16, 'M': 16, 'n': 17, 'N': 17, 'o': 18, 'O': 18, 'p': 20, 'P': 20,
    'r': 21, 'R': 21, 's': 22, 'S': 22, 't': 23, 'T': 23, 'u': 24, 'U': 24,
    'w': 25, 'W': 25, 'x': 26, 'X': 26, 'y': 27, 'Y': 27, 'z': 28, 'Z': 28,
    'Return': 40,
    'space': 44,
    'BackSpace': 42
}

class NativeKVM(Gtk.Window):
    def __init__(self):
        super().__init__(title="Native Wayland KVM")

        # 1. True Wayland Fullscreen
        self.fullscreen()

        # 2. Enable Native Compositor Transparency
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        # Set 10% opacity (Works flawlessly in Wayland)
        self.set_opacity(0.10)

        # 3. Tell GTK exactly which hardware events we want to listen to
        self.add_events(
            Gdk.EventMask.KEY_PRESS_MASK |
            Gdk.EventMask.KEY_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK
        )

        # 4. Bind the events to our functions
        self.connect("key-press-event", self.on_press)
        self.connect("key-release-event", self.on_release)
        self.connect("motion-notify-event", self.on_move)
        self.connect("button-press-event", self.on_click)
        self.connect("button-release-event", self.on_release_click)
        self.connect("destroy", Gtk.main_quit)

        self.last_x = None
        self.last_y = None
        self.mouse_btns = 0

        # Open USB endpoints
        try:
            self.hid_kb = open('/dev/hidg0', 'wb')
            self.hid_mouse = open('/dev/hidg1', 'wb')
        except FileNotFoundError:
            print("[ERROR] USB Gadget files not found!")
            exit(1)

    # --- USB FUNCTIONS ---
    def send_kb(self, hid_code):
        report = bytearray(8)
        report[2] = hid_code
        try:
            self.hid_kb.write(report)
            self.hid_kb.flush()
        except (BrokenPipeError, BlockingIOError):
            pass

    def send_mouse(self, dx, dy):
        dx = max(-127, min(127, int(dx)))
        dy = max(-127, min(127, int(dy)))
        report = bytearray([self.mouse_btns, dx & 0xFF, dy & 0xFF, 0])
        try:
            self.hid_mouse.write(report)
            self.hid_mouse.flush()
        except (BrokenPipeError, BlockingIOError):
            pass

    # --- INPUT CAPTURE ---
    def on_press(self, widget, event):
        # Convert GTK key event to a string (e.g., 'a', 'Return', 'Escape')
        keyname = Gdk.keyval_name(event.keyval)

        # Kill Switch!
        if keyname == 'Escape':
            print("[INFO] Escape pressed. Exiting KVM...")
            Gtk.main_quit()
            return True

        usb_code = KEYMAP.get(keyname, 0)
        if usb_code != 0:
            self.send_kb(usb_code)
        return True

    def on_release(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname in KEYMAP:
            self.send_kb(0)
        return True

    def on_move(self, widget, event):
        if self.last_x is not None and self.last_y is not None:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            if dx != 0 or dy != 0:
                self.send_mouse(dx, dy)
        self.last_x, self.last_y = event.x, event.y
        return True

    def on_click(self, widget, event):
        # Middle Mouse Button Kill Switch
        if event.button == 2:
            print("[INFO] Middle click detected. Exiting KVM...")
            Gtk.main_quit()
            return True

        if event.button == 1: self.mouse_btns = 1
        elif event.button == 3: self.mouse_btns = 2
        self.send_mouse(0, 0)
        return True

    def on_release_click(self, widget, event):
        self.mouse_btns = 0
        if event.button != 2:
            self.send_mouse(0, 0)
        return True

if __name__ == "__main__":
    print("[INFO] Native Wayland KVM Starting...")
    print("[INFO] Press 'ESC' or click the MIDDLE MOUSE BUTTON to exit.")

    app = NativeKVM()
    app.show_all()
    Gtk.main()