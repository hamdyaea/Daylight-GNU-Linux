#!/usr/bin/env python3
"""Native wlroots pointer input for disposable compositor integration tests.

Copyright (C) 2026 Hamdy Abou El Anein — GPL-3.0-only.

Uses zwlr_virtual_pointer_manager_v1 directly through a Wayland socket. No XTest,
Tk event generation, surfaces, output configuration or third-party bindings are
involved. Coordinates use the complete compositor's logical coordinate extent.
Protocol: wlr-protocols/unstable/wlr-virtual-pointer-unstable-v1.xml.
"""
import argparse
import json
import os
from pathlib import Path
import socket
import struct
import sys
import time


def _words(*values):
    return struct.pack("=" + "I" * len(values), *values)


def _string(value):
    data = value.encode("utf-8") + b"\0"
    return _words(len(data)) + data + b"\0" * (-len(data) % 4)


def _read_string(payload, offset):
    if offset + 4 > len(payload):
        raise RuntimeError("Truncated Wayland string length")
    length, = struct.unpack_from("=I", payload, offset)
    offset += 4
    padded_length = (length + 3) // 4 * 4
    if length < 1 or offset + padded_length > len(payload):
        raise RuntimeError("Invalid Wayland string")
    if payload[offset + length - 1] != 0:
        raise RuntimeError("Unterminated Wayland string")
    value = payload[offset:offset + length - 1].decode("utf-8", errors="replace")
    return value, offset + padded_length


class _Wayland:
    def __init__(self, display=None):
        path = Path(display or os.environ.get("WAYLAND_DISPLAY", "wayland-0"))
        if not path.is_absolute():
            runtime = os.environ.get("XDG_RUNTIME_DIR")
            if not runtime:
                raise RuntimeError("XDG_RUNTIME_DIR is missing")
            path = Path(runtime) / path
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.socket.settimeout(4)
        self.buffer = b""
        self.next_id = 3
        self.globals = {}
        try:
            self.socket.connect(str(path))
            self.send(1, 1, _words(2))  # wl_display.get_registry(new_id)
            self.roundtrip()
        except BaseException:
            self.socket.close()
            raise

    def allocate(self):
        result = self.next_id
        self.next_id += 1
        return result

    def send(self, target, opcode, payload=b""):
        size = 8 + len(payload)
        if size % 4 or size > 65532:
            raise ValueError("Invalid Wayland request size")
        self.socket.sendall(_words(target, size << 16 | opcode) + payload)

    def event(self):
        while len(self.buffer) < 8:
            self._receive()
        target, packed = struct.unpack_from("=II", self.buffer)
        size, opcode = packed >> 16, packed & 65535
        if size < 8 or size % 4:
            raise RuntimeError("Invalid Wayland event header")
        while len(self.buffer) < size:
            self._receive()
        payload, self.buffer = self.buffer[8:size], self.buffer[size:]
        if target == 1 and opcode == 0:  # wl_display.error
            if len(payload) < 8:
                raise RuntimeError("Truncated Wayland protocol error")
            object_id, code = struct.unpack_from("=II", payload)
            detail, _ = _read_string(payload, 8)
            raise RuntimeError(f"Wayland protocol error object={object_id} code={code}: {detail}")
        if target == 2 and opcode == 0:  # wl_registry.global
            if len(payload) < 4:
                raise RuntimeError("Truncated Wayland registry event")
            name, = struct.unpack_from("=I", payload)
            interface, pos = _read_string(payload, 4)
            if pos + 4 > len(payload):
                raise RuntimeError("Missing Wayland global version")
            version, = struct.unpack_from("=I", payload, pos)
            self.globals[name] = {"name": name, "interface": interface, "version": version}
        if target == 2 and opcode == 1:  # wl_registry.global_remove
            if len(payload) != 4:
                raise RuntimeError("Invalid Wayland global removal")
            name, = struct.unpack_from("=I", payload)
            self.globals.pop(name, None)
        return target, opcode, payload

    def _receive(self):
        chunk = self.socket.recv(65536)
        if not chunk:
            raise RuntimeError("Wayland connection closed")
        self.buffer += chunk

    def roundtrip(self):
        callback = self.allocate()
        self.send(1, 0, _words(callback))  # wl_display.sync
        while True:
            target, opcode, _ = self.event()
            if target == callback and opcode == 0:
                return

    def bind(self, entry):
        object_id = self.allocate()
        self.send(2, 0, _words(entry["name"]) + _string(entry["interface"]) +
                  _words(1, object_id))
        return object_id

    def close(self):
        self.socket.close()


class NativePointer:
    """Context-managed native pointer; ``click(x, y, width, height)`` sends input.

    Keep the target application's event loop running while using the pointer, or
    pump it after each call. ``close`` releases any held button and destroys only
    this helper's virtual pointer and manager objects.
    """

    def __init__(self, display=None):
        self.connection = _Wayland(display)
        self.manager = self.pointer = None
        self.pressed = False
        self.closed = False
        try:
            entry = next((entry for entry in self.connection.globals.values()
                          if entry["interface"] == "zwlr_virtual_pointer_manager_v1"), None)
            if entry is None:
                raise RuntimeError("Compositor does not advertise zwlr_virtual_pointer_manager_v1")
            self.manager = self.connection.bind(entry)
            self.pointer = self.connection.allocate()
            self.connection.send(self.manager, 0, _words(0, self.pointer))
            self.connection.roundtrip()
        except BaseException:
            self.connection.close()
            self.closed = True
            raise

    def __enter__(self):
        return self

    def __exit__(self, kind, error, traceback):
        try:
            self.close()
        except (OSError, RuntimeError):
            if kind is None:
                raise

    @staticmethod
    def _timestamp():
        return int(time.monotonic() * 1000) & 0xffffffff

    def _button(self, state):
        # Linux evdev BTN_LEFT; Wayland pressed=1, released=0.
        self.connection.send(self.pointer, 2, _words(self._timestamp(), 0x110, state))
        self.connection.send(self.pointer, 4)  # zwlr_virtual_pointer_v1.frame
        self.connection.roundtrip()

    def move(self, x, y, width, height):
        if self.closed:
            raise RuntimeError("Native pointer is closed")
        if any(not isinstance(value, int) or isinstance(value, bool)
               for value in (x, y, width, height)):
            raise ValueError("Pointer coordinates and extent must be integers")
        if width <= 0 or height <= 0 or not 0 <= x <= width or not 0 <= y <= height:
            raise ValueError("Position must be inside the positive coordinate extents")
        self.connection.send(self.pointer, 1, _words(self._timestamp(), x, y, width, height))
        self.connection.send(self.pointer, 4)
        self.connection.roundtrip()
        # Let Xwayland process pointer enter before the first button event.
        time.sleep(.15)

    def click(self, x, y, width, height, hold_ms=80):
        if not isinstance(hold_ms, int) or not 20 <= hold_ms <= 1000:
            raise ValueError("hold_ms must be between 20 and 1000")
        self.move(x, y, width, height)
        self.pressed = True
        try:
            # Keep the requested position and press in the same input frame.
            # Xwayland may warp the seat after the earlier enter roundtrip.
            self.connection.send(self.pointer, 1, _words(self._timestamp(), x, y, width, height))
            self._button(1)
            time.sleep(hold_ms / 1000)
        finally:
            self._button(0)
            self.pressed = False
        time.sleep(.15)

    def close(self):
        if self.closed:
            return
        try:
            if self.pressed:
                self._button(0)
                self.pressed = False
            self.connection.send(self.pointer, 8)  # virtual_pointer.destroy
            self.connection.send(self.manager, 1)  # virtual_pointer_manager.destroy
            self.connection.roundtrip()
        finally:
            self.closed = True
            self.connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--display", help="Wayland socket name or absolute path")
    parser.add_argument("--list", action="store_true", help="List compositor globals only")
    parser.add_argument("--x", type=int)
    parser.add_argument("--y", type=int)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    parser.add_argument("--click", action="store_true", help="Send left press and release after movement")
    parser.add_argument("--hold-ms", type=int, default=80)
    args = parser.parse_args()
    if args.list:
        connection = _Wayland(args.display)
        try:
            print(json.dumps(list(connection.globals.values()), indent=2))
        finally:
            connection.close()
        return
    if None in (args.x, args.y, args.width, args.height):
        parser.error("Supply --x, --y, --width and --height, or use --list")
    with NativePointer(args.display) as pointer:
        if args.click:
            pointer.click(args.x, args.y, args.width, args.height, args.hold_ms)
        else:
            pointer.move(args.x, args.y, args.width, args.height)
    print(json.dumps({"native_wayland_pointer": "click" if args.click else "move",
                      "x": args.x, "y": args.y, "extent": [args.width, args.height]}))


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
