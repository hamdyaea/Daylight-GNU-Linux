#!/usr/bin/env python3
"""Read-only X11 window, stacking and pointer snapshot for an isolated DISPLAY.

Uses only Python's standard library, libX11 queries and read-only xprop calls.
No window properties, geometry, stacking, input focus or input are changed.
"""
# Copyright (C) 2026 Hamdy Abou El Anein
# SPDX-License-Identifier: GPL-3.0-only
import argparse
import ctypes as C
from ctypes.util import find_library
import json
import os
import subprocess


Window = C.c_ulong
Display = C.c_void_p
Bool = C.c_int


class XWindowAttributes(C.Structure):
    _fields_ = [
        ("x", C.c_int), ("y", C.c_int), ("width", C.c_int), ("height", C.c_int),
        ("border_width", C.c_int), ("depth", C.c_int), ("visual", C.c_void_p),
        ("root", Window), ("window_class", C.c_int), ("bit_gravity", C.c_int),
        ("win_gravity", C.c_int), ("backing_store", C.c_int),
        ("backing_planes", C.c_ulong), ("backing_pixel", C.c_ulong),
        ("save_under", Bool), ("colormap", C.c_ulong), ("map_installed", Bool),
        ("map_state", C.c_int), ("all_event_masks", C.c_long),
        ("your_event_mask", C.c_long), ("do_not_propagate_mask", C.c_long),
        ("override_redirect", Bool), ("screen", C.c_void_p),
    ]


class XErrorEvent(C.Structure):
    _fields_ = [("type", C.c_int), ("display", Display), ("resourceid", Window),
                ("serial", C.c_ulong), ("error_code", C.c_ubyte),
                ("request_code", C.c_ubyte), ("minor_code", C.c_ubyte)]


def _xid(value):
    return f"0x{int(value):x}"


def _library():
    library = C.CDLL(find_library("X11") or "libX11.so.6")
    signatures = {
        "XOpenDisplay": ([C.c_char_p], Display),
        "XCloseDisplay": ([Display], C.c_int),
        "XDefaultRootWindow": ([Display], Window),
        "XQueryTree": ([Display, Window, C.POINTER(Window), C.POINTER(Window),
                        C.POINTER(C.POINTER(Window)), C.POINTER(C.c_uint)], C.c_int),
        "XGetWindowAttributes": ([Display, Window, C.POINTER(XWindowAttributes)], C.c_int),
        "XQueryPointer": ([Display, Window, C.POINTER(Window), C.POINTER(Window),
                           C.POINTER(C.c_int), C.POINTER(C.c_int),
                           C.POINTER(C.c_int), C.POINTER(C.c_int),
                           C.POINTER(C.c_uint)], Bool),
        "XFree": ([C.c_void_p], C.c_int),
        "XSync": ([Display, Bool], C.c_int),
        "XSetErrorHandler": ([C.c_void_p], C.c_void_p),
    }
    for name, (arguments, returns) in signatures.items():
        function = getattr(library, name)
        function.argtypes, function.restype = arguments, returns
    return library


def snapshot(tk_ids=None):
    """Return a JSON-serializable read-only snapshot under the current DISPLAY.

    ``tk_ids`` can contain integer IDs or hexadecimal strings returned by Tk's
    ``winfo_id()`` or ``wm frame``. Windows may disappear during the snapshot;
    their query failures are included rather than mutating or retrying them.
    XQueryTree orders children from the bottom to the top of the X11 stack.
    """
    library = _library()
    display_name = os.environ.get("DISPLAY")
    display = library.XOpenDisplay(display_name.encode() if display_name else None)
    if not display:
        raise RuntimeError(f"Cannot open X11 DISPLAY {display_name!r}")
    errors = []
    error_type = C.CFUNCTYPE(C.c_int, Display, C.POINTER(XErrorEvent))

    @error_type
    def on_error(_display, event):
        record = event.contents
        errors.append({"resource": _xid(record.resourceid), "error_code": int(record.error_code),
                       "request_code": int(record.request_code), "minor_code": int(record.minor_code),
                       "serial": int(record.serial)})
        return 0

    previous_handler = library.XSetErrorHandler(C.cast(on_error, C.c_void_p))
    root = int(library.XDefaultRootWindow(display))

    def tree(window):
        queried_root, parent = Window(), Window()
        children, count = C.POINTER(Window)(), C.c_uint()
        success = library.XQueryTree(display, window, C.byref(queried_root), C.byref(parent),
                                    C.byref(children), C.byref(count))
        if not success:
            return {"id": _xid(window), "query_failed": True}
        try:
            return {"id": _xid(window), "root": _xid(queried_root.value),
                    "parent": _xid(parent.value),
                    "children_bottom_to_top": [_xid(children[index]) for index in range(count.value)]}
        finally:
            if children:
                library.XFree(children)

    def attributes(window):
        values = XWindowAttributes()
        if not library.XGetWindowAttributes(display, window, C.byref(values)):
            return {"id": _xid(window), "query_failed": True}
        return {"id": _xid(window), "root": _xid(values.root),
                "geometry_relative_to_parent": {name: int(getattr(values, name)) for name in
                                                ("x", "y", "width", "height", "border_width", "depth")},
                "class": {1: "InputOutput", 2: "InputOnly"}.get(values.window_class, values.window_class),
                "map_state": {0: "IsUnmapped", 1: "IsUnviewable", 2: "IsViewable"}.get(values.map_state, values.map_state),
                "override_redirect": bool(values.override_redirect),
                "all_event_masks": int(values.all_event_masks),
                "your_event_mask": int(values.your_event_mask),
                "do_not_propagate_mask": int(values.do_not_propagate_mask)}

    def pointer(window):
        queried_root, child = Window(), Window()
        root_x, root_y, win_x, win_y = (C.c_int() for _ in range(4))
        mask = C.c_uint()
        same_screen = library.XQueryPointer(display, window, C.byref(queried_root), C.byref(child),
                                            C.byref(root_x), C.byref(root_y), C.byref(win_x),
                                            C.byref(win_y), C.byref(mask))
        return {"window": _xid(window), "same_screen": bool(same_screen),
                "root": _xid(queried_root.value), "child_under_pointer": _xid(child.value),
                "root_xy": [root_x.value, root_y.value], "window_xy": [win_x.value, win_y.value],
                "mask": mask.value, "attributes": attributes(window)}

    try:
        root_tree = tree(root)
        child_stack = [attributes(int(value, 16)) for value in root_tree.get("children_bottom_to_top", [])]
        hierarchies = []
        for item in tk_ids or []:
            window = int(item, 0) if isinstance(item, str) else int(item)
            ancestry, visited = [], set()
            while window and window not in visited and len(ancestry) < 64:
                visited.add(window)
                relation = tree(window)
                ancestry.append({"tree": relation, "attributes": attributes(window)})
                window = int(relation.get("parent", "0x0"), 16)
            hierarchies.append({"requested": _xid(int(item, 0) if isinstance(item, str) else item),
                                "ancestors_inner_to_root": ancestry})
        descent, visited, window = [], set(), root
        while window and window not in visited and len(descent) < 64:
            visited.add(window)
            record = pointer(window)
            descent.append(record)
            if not record["same_screen"]:
                break
            window = int(record["child_under_pointer"], 16)
        try:
            properties = subprocess.run(
                ["xprop", "-root", "_NET_CLIENT_LIST_STACKING", "_NET_CLIENT_LIST", "_NET_ACTIVE_WINDOW"],
                capture_output=True, text=True, timeout=5)
            ewmh = {"returncode": properties.returncode, "stdout": properties.stdout,
                    "stderr": properties.stderr}
        except (OSError, subprocess.TimeoutExpired) as error:
            ewmh = {"error": str(error)}
        library.XSync(display, 0)
        return {"display": display_name, "root": _xid(root), "root_attributes": attributes(root),
                "root_tree": root_tree, "root_child_stack_bottom_to_top": child_stack,
                "ewmh_xprop": ewmh, "tk_hierarchies": hierarchies,
                "pointer_descent": descent,
                "deepest_pointer_window": descent[-1]["window"] if descent else None,
                "x11_errors": errors}
    finally:
        library.XSync(display, 0)
        library.XCloseDisplay(display)
        library.XSetErrorHandler(previous_handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tk_ids", nargs="*", help="Optional Tk inner/frame window IDs, hexadecimal or decimal")
    args = parser.parse_args()
    print(json.dumps(snapshot(args.tk_ids), indent=2))


if __name__ == "__main__":
    main()
