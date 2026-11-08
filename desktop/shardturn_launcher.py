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
            panel = tk.Frame(self.root, bg=resources.BG)
            self.help_window = panel
            escape_binding = None

            def cleanup():
                nonlocal escape_binding
                if escape_binding is not None:
                    self.root.unbind("<Escape>", escape_binding)
                    escape_binding = None
                if self.help_window is panel:
                    self.help_window = None
                try:
                    panel.grab_release()
                except tk.TclError:
                    pass

            def closed():
                cleanup()
                panel.destroy()
                self.canvas.focus_set()
                self.refresh()

            def escaped(_event):
                closed()
                return "break"

            def destroyed(event):
                if event.widget is panel:
                    cleanup()

            panel.bind("<Destroy>", destroyed, add="+")
            try:
                header = tk.Frame(panel, bg=resources.BG)
                header.pack(fill="x", padx=24, pady=(16, 0))
                tk.Label(header, text="Rules and controls · Shardturn",
                         bg=resources.BG, fg=resources.INK,
                         font=(resources.FONT_FAMILY, 14, "bold")).pack(side="left")
                tk.Button(header, text="Close  ·  Esc", command=closed,
                          bg=resources.BG, fg=resources.INK,
                          font=(resources.FONT_FAMILY, 11), padx=12, pady=6).pack(side="right")
                bar = tk.Scrollbar(panel)
                bar.pack(side="right", fill="y")
                text = tk.Text(panel, bg=resources.BG, fg=resources.INK,
                               font=(resources.FONT_FAMILY, 11), wrap="word",
                               padx=24, pady=24, relief="flat",
                               yscrollcommand=bar.set, selectbackground="#446c70")
                text.pack(fill="both", expand=True)
                bar.configure(command=text.yview)
                text.insert("1.0", resources.RULES)
                text.configure(state="disabled")
                escape_binding = self.root.bind("<Escape>", escaped, add="+")
                panel.place(x=0, y=0, relwidth=1, relheight=1)
                panel.lift()
                panel.update_idletasks()
                if not panel.winfo_viewable():
                    panel.wait_visibility()
                panel.grab_set()
                text.focus_set()
            except BaseException:
                cleanup()
                panel.destroy()
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
