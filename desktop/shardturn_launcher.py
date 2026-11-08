#!/usr/bin/env python3
"""Launch the unchanged Shardturn game with Daylight's Tk window preparation.

Copyright (C) 2026 Hamdy Abou El Anein
SPDX-License-Identifier: GPL-3.0-only
"""
import argparse
import importlib.util
from pathlib import Path
import sys
import tkinter as tk

from daylight_ui import windowing


def _game_module():
    path = Path("/usr/share/daylight/shardturn/Shardturn.py")
    if not path.is_file():
        path = Path(__file__).resolve().parent / "shardturn/Shardturn.py"
    spec = importlib.util.spec_from_file_location("daylight_shardturn", path)
    if spec is None or spec.loader is None:
        raise ImportError("Shardturn is not installed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def create_app(seed=None):
    module = _game_module()
    root = tk.Tk()
    windowing.prepare(root)
    try:
        app = module.ShardturnApp(root, seed=seed)
        windowing.finish(root)
        return root, app
    except BaseException:
        root.destroy()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    root, _app = create_app(seed=args.seed)
    root.mainloop()


if __name__ == "__main__":
    main()
