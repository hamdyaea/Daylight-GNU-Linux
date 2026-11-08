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


def _windowed_game_class(original):
    resources = sys.modules[original.__module__]

    class DaylightShardturn(original):
        def show_help(self):
            if self.help_window:
                self.help_window.lift()
                return
            self.cancel_ai()
            top = tk.Toplevel(self.root)
            top.withdraw()
            self.help_window = top
            try:
                top.title("Rules and controls · Shardturn")
                top.geometry("760x690")
                top.configure(bg=resources.BG)
                top.transient(self.root)
                bar = tk.Scrollbar(top)
                bar.pack(side="right", fill="y")
                text = tk.Text(top, bg=resources.BG, fg=resources.INK,
                               font=(resources.FONT_FAMILY, 11), wrap="word",
                               padx=24, pady=24, relief="flat",
                               yscrollcommand=bar.set, selectbackground="#446c70")
                text.pack(fill="both", expand=True)
                bar.configure(command=text.yview)
                text.insert("1.0", resources.RULES)
                text.configure(state="disabled")

                def closed():
                    self.help_window = None
                    top.destroy()
                    self.refresh()

                top.protocol("WM_DELETE_WINDOW", closed)
                top.bind("<Escape>", lambda _event: closed())
                # Settle all content and transient geometry before the first
                # map; an Xwayland grab must use that final surface origin.
                top.update_idletasks()
                top.deiconify()
                top.wait_visibility()
                top.grab_set()
            except BaseException:
                self.help_window = None
                top.destroy()
                self.refresh()
                raise
    return DaylightShardturn


def create_app(seed=None):
    module = _game_module()
    root = tk.Tk()
    windowing.prepare(root)
    try:
        app = _windowed_game_class(module.ShardturnApp)(root, seed=seed)
        windowing.finish(root)
        return root, app
    except BaseException:
        root.destroy()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int)
    args = parser.parse_args()
    from daylight_ui.state import ensure_session_manager
    ensure_session_manager()
    root, _app = create_app(seed=args.seed)
    root.mainloop()


if __name__ == "__main__":
    main()
