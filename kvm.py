import gi
import os
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

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

        self.fullscreen()
        self.set_app_paintable(True)
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.set_opacity(0.10)

        self.add_events(
            Gdk.EventMask.KEY_PRESS_MASK |
            Gdk.EventMask.KEY_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK
        )

        self.connect("key-press-event", self.on_press)
        self.connect("key-release-event", self.on_release)
        self.connect("motion-notify-event", self.on_move)
        self.connect("button-press-event", self.on_click)
        self.connect("button-release-event", self.on_release_click)
        self.connect("destroy", Gtk.main_quit)

        # Tracker Variables for the Sync Burst
        self.current_x = 0
        self.current_y = 0
        self.sync_counter = 0
        self.mouse_btns = 0

        # Start the 300ms heartbeat
        GLib.timeout_add(300, self.sync_mouse)

        # Open USB endpoints
        try:
            self.hid_kb = open('/dev/hidg0', 'wb')
            self.hid_mouse = open('/dev/hidg1', 'wb')
        except FileNotFoundError:
            print("[ERROR] USB Gadget files not found!")
            exit(1)

    def send_kb(self, hid_code):
        report = bytearray(8)
        report[2] = hid_code
        try:
            self.hid_kb.write(report)
            self.hid_kb.flush()
        except (BrokenPipeError, BlockingIOError):
            pass

    def send_mouse(self, x, y):
        # 1. Convert local 1920x1080 pixel coordinates into global percentages
        # 2. Map that percentage to the 0-32767 absolute USB grid
        abs_x = int((x / 1920.0) * 32767)
        abs_y = int((y / 1080.0) * 32767)

        abs_x = max(0, min(32767, abs_x))
        abs_y = max(0, min(32767, abs_y))

        # 5-byte Absolute Mouse Report
        report = bytearray([
            self.mouse_btns,
            abs_x & 0xFF,
            (abs_x >> 8) & 0xFF,
            abs_y & 0xFF,
            (abs_y >> 8) & 0xFF
        ])

        try:
            self.hid_mouse.write(report)
            self.hid_mouse.flush()
        except (BrokenPipeError, BlockingIOError):
            pass

    def on_move(self, widget, event):
        # Record current position
        self.current_x = event.x
        self.current_y = event.y

        # Send immediately for lowest latency
        self.send_mouse(self.current_x, self.current_y)

        # Queue 10 additional "anchor" pulses for when the mouse stops moving
        self.sync_counter = 20
        return True

    def sync_mouse(self):
        # This function runs every 300ms unconditionally
        if self.sync_counter > 0:
            self.send_mouse(self.current_x, self.current_y)
            self.sync_counter -= 1
        return True

    def on_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
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

    def on_click(self, widget, event):
        if event.button == 2:
            print("[INFO] Middle click detected. Exiting KVM...")
            Gtk.main_quit()
            return True

        if event.button == 1: self.mouse_btns = 1
        elif event.button == 3: self.mouse_btns = 2

        # Immediately push the click state
        self.send_mouse(self.current_x, self.current_y)
        return True

    def on_release_click(self, widget, event):
        self.mouse_btns = 0
        if event.button != 2:
            self.send_mouse(self.current_x, self.current_y)
        return True

if __name__ == "__main__":
    print("[INFO] Native Wayland KVM Starting...")
    print(f"[INFO] Process ID (PID): {os.getpid()}")
    print("[INFO] Press 'ESC' or click the MIDDLE MOUSE BUTTON to exit.")

    app = NativeKVM()
    app.show_all()
    Gtk.main()