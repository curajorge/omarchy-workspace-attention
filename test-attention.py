#!/usr/bin/env python3
"""Manual XWayland urgency test. Requires Python 3, libX11, and DISPLAY."""
import ctypes as c
import ctypes.util
import os
import json
import subprocess
import time


class WMHints(c.Structure):
    _fields_ = [
        ("flags", c.c_long), ("input", c.c_int), ("initial_state", c.c_int),
        ("icon_pixmap", c.c_ulong), ("icon_window", c.c_ulong),
        ("icon_x", c.c_int), ("icon_y", c.c_int),
        ("icon_mask", c.c_ulong), ("window_group", c.c_ulong),
    ]


class ClientData(c.Union):
    _fields_ = [("b", c.c_char * 20), ("s", c.c_short * 10), ("l", c.c_long * 5)]


class ClientMessage(c.Structure):
    _fields_ = [("type", c.c_int), ("serial", c.c_ulong), ("send_event", c.c_int),
                ("display", c.c_void_p), ("window", c.c_ulong),
                ("message_type", c.c_ulong), ("format", c.c_int), ("data", ClientData)]


class XEvent(c.Union):
    _fields_ = [("client", ClientMessage), ("pad", c.c_long * 24)]


class ClassHint(c.Structure):
    _fields_ = [("res_name", c.c_char_p), ("res_class", c.c_char_p)]


def main():
    try:
        focus_setting = json.loads(subprocess.check_output(
            ["hyprctl", "getoption", "misc:focus_on_activate", "-j"], text=True))
    except (OSError, subprocess.CalledProcessError, ValueError):
        raise SystemExit("Cannot verify Hyprland's focus_on_activate setting; aborting test.")
    if focus_setting.get("bool", focus_setting.get("int")) not in (False, 0):
        raise SystemExit("Set misc.focus_on_activate=false before this test to avoid focus switching.")
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
        "XSetClassHint": (c.c_int, [c.c_void_p, c.c_ulong, c.POINTER(ClassHint)]),
        "XSetWMHints": (c.c_int, [c.c_void_p, c.c_ulong, c.POINTER(WMHints)]),
        "XFlush": (c.c_int, [c.c_void_p]),
        "XInternAtom": (c.c_ulong, [c.c_void_p, c.c_char_p, c.c_int]),
        "XSendEvent": (c.c_int, [c.c_void_p, c.c_ulong, c.c_int, c.c_long, c.POINTER(XEvent)]),
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
        class_hint = ClassHint(b"workspace-attention-test", b"WorkspaceAttentionTest")
        x.XSetClassHint(display, window, c.byref(class_hint))
        x.XStoreName(display, window, b"Attention test - switch to another workspace now")
        x.XMapWindow(display, window)
        x.XFlush(display)
        print("Switch to another workspace within 10 seconds.", flush=True)
        time.sleep(10)
        hints = WMHints()
        hints.flags = 1 << 8  # ICCCM XUrgencyHint; does not request focus.
        x.XStoreName(display, window, b"Attention test - focus this window to clear the indicator")
        x.XSetWMHints(display, window, c.byref(hints))
        event = XEvent()
        event.client.type = 33  # ClientMessage
        event.client.display = display
        event.client.window = window
        event.client.message_type = x.XInternAtom(display, b"_NET_WM_STATE", 0)
        event.client.format = 32
        event.client.data.l[0] = 1  # _NET_WM_STATE_ADD
        event.client.data.l[1] = x.XInternAtom(display, b"_NET_WM_STATE_DEMANDS_ATTENTION", 0)
        event.client.data.l[3] = 1  # Application source
        x.XSendEvent(display, x.XDefaultRootWindow(display), 0,
                     (1 << 20) | (1 << 19), c.byref(event))
        # Hyprland marks rejected activation requests urgent. Keep
        # misc.focus_on_activate=false when running this manual test.
        activation = XEvent()
        activation.client.type = 33
        activation.client.display = display
        activation.client.window = window
        activation.client.message_type = x.XInternAtom(display, b"_NET_ACTIVE_WINDOW", 0)
        activation.client.format = 32
        activation.client.data.l[0] = 1
        x.XSendEvent(display, x.XDefaultRootWindow(display), 0,
                     (1 << 20) | (1 << 19), c.byref(activation))
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
