"""Shared Shardturn-inspired colour, typography and geometry.

SPDX-License-Identifier: GPL-3.0-only
"""
import tkinter as tk
from tkinter import ttk

LIGHT = dict(bg="#e9e6df", panel="#faf8f2", card="#fcfaf5", ink="#292a43",
             muted="#66667b", line="#d7d2c8", accent="#6548a3", night="#292c49",
             coral="#ce6655", amber="#c79a36", jade="#358d7d", iris="#7c6fbb")
DARK = dict(LIGHT, bg="#202337", panel="#292c49", card="#323651", ink="#f3f0e8",
            muted="#c0bfd0", line="#484c67", accent="#b3a0e0", night="#171b2c")
PALETTE = dict(LIGHT)


def apply(root, appearance="light", text_scale=1.0):
    PALETTE.update(DARK if appearance == "dark" else LIGHT)
    p = PALETTE
    size = max(10, round(11 * text_scale))
    root.configure(bg=p["bg"])
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure(".", font=("DejaVu Sans", size), background=p["bg"],
                    foreground=p["ink"], bordercolor=p["line"], focuscolor=p["accent"])
    style.configure("TFrame", background=p["bg"])
    style.configure("Card.TFrame", background=p["panel"])
    style.configure("TLabel", background=p["bg"], foreground=p["ink"])
    style.configure("Card.TLabel", background=p["panel"])
    style.configure("Muted.TLabel", foreground=p["muted"])
    style.configure("Title.TLabel", font=("DejaVu Sans", round(26 * text_scale), "bold"))
    style.configure("Heading.TLabel", font=("DejaVu Sans", round(15 * text_scale), "bold"))
    style.configure("TButton", padding=(14, 10), background=p["panel"], foreground=p["ink"],
                    borderwidth=1, relief="flat", focusthickness=2)
    style.map("TButton", background=[("active", p["line"]), ("pressed", p["line"])])
    style.configure("Accent.TButton", background=p["accent"], foreground=p["bg"])
    style.map("Accent.TButton", background=[("active", p["iris"])], foreground=[("active", "white")])
    style.configure("TEntry", fieldbackground=p["card"], foreground=p["ink"], padding=9)
    style.configure("TCombobox", fieldbackground=p["card"], foreground=p["ink"], padding=7)
    style.map("TCombobox", fieldbackground=[("readonly", p["card"])],
              foreground=[("readonly", p["ink"])])
    style.configure("TCheckbutton", background=p["bg"], foreground=p["ink"], padding=5)
    style.map("TCheckbutton", background=[("active", p["bg"])])
    style.configure("TRadiobutton", background=p["bg"], foreground=p["ink"], padding=5)
    style.configure("TNotebook", background=p["bg"], tabmargins=(0, 8, 0, 0))
    style.configure("TNotebook.Tab", padding=(16, 10))
    style.configure("Treeview", background=p["card"], fieldbackground=p["card"],
                    foreground=p["ink"], rowheight=32)
    style.map("Treeview", background=[("selected", p["accent"])], foreground=[("selected", "white")])
    style.configure("Treeview.Heading", background=p["panel"], font=("DejaVu Sans", size, "bold"))
    style.configure("Horizontal.TProgressbar", background=p["jade"], troughcolor=p["line"])


def panel(parent, **kwargs):
    return ttk.Frame(parent, style="Card.TFrame", padding=kwargs.pop("padding", 18), **kwargs)


def label(parent, text, kind="body", **kwargs):
    styles = {"title": "Title.TLabel", "heading": "Heading.TLabel", "muted": "Muted.TLabel"}
    return ttk.Label(parent, text=text, style=styles.get(kind, "TLabel"), **kwargs)


def button(parent, text, command, primary=False, **kwargs):
    return ttk.Button(parent, text=text, command=command,
                      style="Accent.TButton" if primary else "TButton", **kwargs)


def emblem(canvas, x, y, radius=24, color=None):
    """Daylight sun above a tiny mountain, resolution independent."""
    p = PALETTE
    canvas.create_oval(x-radius*.34, y-radius*.8, x+radius*.34, y-radius*.12,
                       fill=color or p["amber"], outline="")
    canvas.create_polygon(x-radius, y+radius*.65, x-radius*.2, y-radius*.16,
                          x+radius*.24, y+radius*.65, fill=p["iris"], outline="")
    canvas.create_polygon(x-radius*.2, y+radius*.65, x+radius*.45, y+radius*.03,
                          x+radius, y+radius*.65, fill=p["jade"], outline="")


def icon(canvas, slug, x=27, y=27, radius=20):
    p = PALETTE
    colors = (p["iris"], p["jade"], p["coral"], p["amber"])
    color = colors[sum(map(ord, slug)) % len(colors)]
    if slug in ("sky", "welcome", "info", "home"):
        emblem(canvas, x, y, radius)
    elif slug in ("cards", "shardturn", "memory"):
        canvas.create_rectangle(x-18, y-19, x+8, y+17, fill=p["card"], outline=color, width=2)
        canvas.create_rectangle(x-7, y-14, x+19, y+22, fill=color, outline="")
        canvas.create_polygon(x+6,y-3,x+13,y+4,x+6,y+11,x-1,y+4,fill=p["card"],outline="")
    elif slug in ("dice", "slots", "lottery", "coin"):
        canvas.create_rectangle(x-18, y-18, x+18, y+18, fill=color, outline="")
        for dx,dy in [(-9,-9),(0,0),(9,9)]:
            canvas.create_oval(x+dx-3,y+dy-3,x+dx+3,y+dy+3,fill=p["card"],outline="")
    elif slug in ("monitor", "doctor", "connect"):
        canvas.create_rectangle(x-22,y-16,x+22,y+13,outline=color,width=3)
        canvas.create_line(x,y+14,x,y+22,x-12,y+22,x+12,y+22,fill=color,width=3)
        canvas.create_line(x-17,y+4,x-9,y-2,x-2,y+4,x+6,y-8,x+16,y-1,fill=color,width=2)
    else:
        canvas.create_polygon(x,y-radius,x+radius,y,x,y+radius,x-radius,y,fill=color,outline="")
        canvas.create_oval(x-6,y-6,x+6,y+6,fill=p["card"],outline="")
