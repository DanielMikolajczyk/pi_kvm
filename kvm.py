import gi
import os
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

# --- BITMASK: MODIFIER KEYS ---
MODIFIERS = {
    'Control_L': 1,   'Shift_L': 2,     'Alt_L': 4,       'Super_L': 8,
    'Control_R': 16,  'Shift_R': 32,    'Alt_R': 64,      'Super_R': 128
}

# --- HEX MAP: STANDARD KEYS ---
KEYMAP = {
    # Alphabet
    'a': 4, 'A': 4, 'b': 5, 'B': 5, 'c': 6, 'C': 6, 'd': 7, 'D': 7,
    'e': 8, 'E': 8, 'f': 9, 'F': 9, 'g': 10, 'G': 10, 'h': 11, 'H': 11,
    'i': 12, 'I': 12, 'j': 13, 'J': 13, 'k': 14, 'K': 14, 'l': 15, 'L': 15,
    'm': 16, 'M': 16, 'n': 17, 'N': 17, 'o': 18, 'O': 18, 'p': 19, 'P': 19,
    'q': 20, 'Q': 20, 'r': 21, 'R': 21, 's': 22, 'S': 22, 't': 23, 'T': 23,
    'u': 24, 'U': 24, 'v': 25, 'V': 25, 'w': 26, 'W': 26, 'x': 27, 'X': 27,
    'y': 28, 'Y': 28, 'z': 29, 'Z': 29,

    # Numbers and their Shifted Symbols
    '1': 30, 'exclam': 30,      '2': 31, 'at': 31,
    '3': 32, 'numbersign': 32,  '4': 33, 'dollar': 33,
    '5': 34, 'percent': 34,     '6': 35, 'asciicircum': 35,
    '7': 36, 'ampersand': 36,   '8': 37, 'asterisk': 37,
    '9': 38, 'parenleft': 38,   '0': 39, 'parenright': 39,

    # Standard Operations
    'Return': 40, 'KP_Enter': 40, 'BackSpace': 42, 'Tab': 43, 'space': 44,

    # Symbols (Base and Shifted)
    'minus': 45, 'underscore': 45,      'equal': 46, 'plus': 46,
    'bracketleft': 47, 'braceleft': 47, 'bracketright': 48, 'braceright': 48,
    'backslash': 49, 'bar': 49,         'semicolon': 51, 'colon': 51,
    'apostrophe': 52, 'quotedbl': 52,   'grave': 53, 'asciitilde': 53,
    'comma': 54, 'less': 54,            'period': 55, 'greater': 55,
    'slash': 56, 'question': 56,

    # Directional Arrows
    'Right': 79, 'Left': 80, 'Down': 81, 'Up': 82
}

class NativeKVM(Gtk.Window):
    def __init__(self):
        super().__init__(title="Native Wayland KVM")

        # UI Setup
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

        # STATE TRACKERS
        self.current_x = 0
        self.current_y = 0
        self.sync_counter = 0
        self.mouse_btns = 0

        # New robust keyboard trackers
        self.current_modifiers = 0
        self.pressed_keys = set()

        # Start the 300ms mouse heartbeat
        GLib.timeout_add(300, self.sync_mouse)

        # Open USB endpoints
        try:
            self.hid_kb = open('/dev/hidg0', 'wb')
            self.hid_mouse = open('/dev/hidg1', 'wb')
        except FileNotFoundError:
            print("[ERROR] USB Gadget files not found!")
            exit(1)

    # --- KEYBOARD LOGIC ---
    def send_kb(self):
        report = bytearray(8)
        report[0] = self.current_modifiers

        # Load up to 6 simultaneously pressed keys into the USB packet
        for index, key_code in enumerate(list(self.pressed_keys)[:6]):
            report[2 + index] = key_code

        try:
            self.hid_kb.write(report)
            self.hid_kb.flush()
        except (BrokenPipeError, BlockingIOError):
            pass

    def on_press(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if not keyname: return True

        if keyname == 'Escape':
            print("[INFO] Escape pressed. Exiting KVM...")
            Gtk.main_quit()
            return True

        # Handle Modifiers (Ctrl, Shift, Alt, Win)
        if keyname in MODIFIERS:
            self.current_modifiers |= MODIFIERS[keyname]
            self.send_kb()
            return True

        # Handle Standard Keys
        usb_code = KEYMAP.get(keyname, 0)
        if usb_code != 0:
            self.pressed_keys.add(usb_code)
            self.send_kb()

        return True

    def on_release(self, widget, event):
        keyname = Gdk.keyval_name(event.keyval)
        if not keyname: return True

        # Handle Modifiers Release
        if keyname in MODIFIERS:
            self.current_modifiers &= ~MODIFIERS[keyname]
            self.send_kb()
            return True

        # Handle Standard Keys Release
        usb_code = KEYMAP.get(keyname, 0)
        if usb_code in self.pressed_keys:
            self.pressed_keys.remove(usb_code)
            self.send_kb()

        return True

    # --- MOUSE LOGIC ---
    def send_mouse(self, x, y):
        abs_x = int((x / 1920.0) * 32767)
        abs_y = int((y / 1080.0) * 32767)

        abs_x = max(0, min(32767, abs_x))
        abs_y = max(0, min(32767, abs_y))

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
        self.current_x = event.x
        self.current_y = event.y
        self.send_mouse(self.current_x, self.current_y)
        self.sync_counter = 10
        return True

    def sync_mouse(self):
        if self.sync_counter > 0:
            self.send_mouse(self.current_x, self.current_y)
            self.sync_counter -= 1
        return True

    def on_click(self, widget, event):
        if event.button == 2:
            print("[INFO] Middle click detected. Exiting KVM...")
            Gtk.main_quit()
            return True

        if event.button == 1: self.mouse_btns |= 1
        elif event.button == 3: self.mouse_btns |= 2

        self.send_mouse(self.current_x, self.current_y)
        return True

    def on_release_click(self, widget, event):
        if event.button == 1: self.mouse_btns &= ~1
        elif event.button == 3: self.mouse_btns &= ~2

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