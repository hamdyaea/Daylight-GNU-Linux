"""Create Tk wrappers before Wayland's XWM can track the temporary inner window.

Copyright (C) 2026 Hamdy Abou El Anein
SPDX-License-Identifier: GPL-3.0-only
"""
from __future__ import annotations

import os
import sys


def enabled(environ=None, platform=None):
    environ = os.environ if environ is None else environ
    platform = sys.platform if platform is None else platform
    return (platform.startswith("linux")
            and environ.get("XDG_SESSION_TYPE", "").lower() == "wayland"
            and bool(environ.get("DISPLAY")))


_TOPLEVEL_HOOK = r"""
namespace eval ::daylight_windowing {}
if {![llength [info commands ::daylight_windowing::original_toplevel]]} {
    rename ::toplevel ::daylight_windowing::original_toplevel
    proc ::toplevel {args} {
        set window [uplevel 1 [linsert $args 0 ::daylight_windowing::original_toplevel]]
        # Embedded or explicitly remote windows belong to their host/display.
        for {set index 1} {$index < [llength $args]} {incr index 2} {
            set option [lindex $args $index]
            if {$option in {-use -screen} && [lindex $args [expr {$index + 1}]] ne ""} {
                return $window
            }
        }
        if {![winfo ismapped $window] && ![wm overrideredirect $window]} {
            wm overrideredirect $window 1
            try {
                winfo id $window
                # Reading -type forces wrapper creation without replacing a hint.
                wm attributes $window -type
            } finally {
                wm overrideredirect $window 0
            }
        }
        # The original MapFrame idle handler retains control of visibility.
        # A caller's withdraw, type, transient and modal setup remain intact.
        return $window
    }
}
"""


def prepare(root):
    """Call immediately after Tk.__init__, before any widgets or font work.

    All attribute changes happen before either window is mapped. X11 sessions
    use Tk's ordinary construction and are left untouched.
    """
    if getattr(root, "_daylight_window_prepared", False):
        return True
    if (not enabled() or root.tk.call("tk", "windowingsystem") != "x11"
            or root.winfo_ismapped()):
        return False
    root.withdraw()
    root.overrideredirect(True)
    try:
        root.winfo_id()
        root.wm_attributes("-type", "normal")
    finally:
        root.overrideredirect(False)
    root.tk.eval(_TOPLEVEL_HOOK)
    root._daylight_window_prepared = True
    return True


def finish(root):
    """Map the completed root; subsequent Toplevels use the Tcl creation hook."""
    if getattr(root, "_daylight_window_prepared", False):
        root.deiconify()
