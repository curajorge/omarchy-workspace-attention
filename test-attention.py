#!/usr/bin/env python3
"""Manual XWayland urgency test. Requires Python 3, libX11, and DISPLAY."""
import ctypes as c
import ctypes.util
import os
import time


class WMHints(c.Structure):
    _fields_ = [
        ("flags", c.c_long), ("input", c.c_int), ("initial_state", c.c_int),
        ("icon_pixmap", c.c_ulong), ("icon_window", c.c_ulong),
        ("icon_x", c.c_int), ("icon_y", c.c_int),
        ("icon_mask", c.c_ulong), ("window_group", c.c_ulong),
    ]


def main():
    if not os.environ.get("DISPLAY"):
        raise SystemExit("Run this from a terminal inside your graphical session (DISPLAY is missing).")
    library = ctypes.util.find_library("X11")
    if not library:
        raise SystemExit("libX11 is required.")
    x = c.CDLL(library)
    signatures = {
        "XOpenDisplay": (c.c_void_p, [c.c_char_p]),
        "XDefaultRootWindow": (c.c_ulong, [c.c_void_p]),
        "XCreateSimpleWindow": (c.c_ulong, [c.c_void_p, c.c_ulong, c.c_int, c.c_int,
                                           c.c_uint, c.c_uint, c.c_uint, c.c_ulong, c.c_ulong]),
        "XStoreName": (c.c_int, [c.c_void_p, c.c_ulong, c.c_char_p]),
        "XMapWindow": (c.c_int, [c.c_void_p, c.c_ulong]),
        "XSetWMHints": (c.c_int, [c.c_void_p, c.c_ulong, c.POINTER(WMHints)]),
        "XFlush": (c.c_int, [c.c_void_p]),
        "XDestroyWindow": (c.c_int, [c.c_void_p, c.c_ulong]),
        "XCloseDisplay": (c.c_int, [c.c_void_p]),
    }
    for name, (result, arguments) in signatures.items():
        function = getattr(x, name)
        function.restype, function.argtypes = result, arguments
    display = x.XOpenDisplay(None)
    if not display:
        raise SystemExit("Cannot connect to XWayland.")
    window = x.XCreateSimpleWindow(display, x.XDefaultRootWindow(display),
                                  0, 0, 420, 160, 0, 0, 0x242424)
    try:
        x.XStoreName(display, window, b"Attention test - switch to another workspace now")
        x.XMapWindow(display, window)
        x.XFlush(display)
        print("Switch to another workspace within 10 seconds.", flush=True)
        time.sleep(10)
        hints = WMHints()
        hints.flags = 1 << 8  # ICCCM XUrgencyHint; does not request focus.
        x.XStoreName(display, window, b"Attention test - focus this window to clear the indicator")
        x.XSetWMHints(display, window, c.byref(hints))
        x.XFlush(display)
        print("Urgency sent. Look for the amber workspace and dot; focus the test window to clear.", flush=True)
        time.sleep(60)
    except KeyboardInterrupt:
        pass
    finally:
        x.XDestroyWindow(display, window)
        x.XCloseDisplay(display)


if __name__ == "__main__":
    main()
