"""
popup.py — Standalone popup window for the ICA Reminder.

Launched as a subprocess by reminder.py so that tkinter always runs on
the main thread of its own process.  Receives the task text via stdin.

Do not run this file directly — it is called by reminder.py.
"""

import sys
import webbrowser
import tkinter as tk
from tkinter import font as tkfont

from ica_reminder.config import (
    NOTIFICATION_TITLE,
    NOTIFICATION_TIMEOUT,
    ICA_URL,
)


def show_popup(task: str) -> None:
    win = tk.Tk()
    win.title(NOTIFICATION_TITLE)
    win.configure(bg="#ffffff")
    win.resizable(False, False)

    # ── Fonts ────────────────────────────────────────────────────────────── #
    title_font = tkfont.Font(family="Segoe UI", size=13, weight="bold")
    body_font  = tkfont.Font(family="Segoe UI", size=11)
    btn_font   = tkfont.Font(family="Segoe UI", size=11, weight="bold")

    # ── Blue header bar ──────────────────────────────────────────────────── #
    tk.Frame(win, bg="#1d4ed8", height=6).pack(fill="x")

    # ── Title ────────────────────────────────────────────────────────────── #
    tk.Label(
        win, text=NOTIFICATION_TITLE,
        font=title_font, bg="#ffffff", fg="#1f2328",
        padx=20, pady=12,
    ).pack(anchor="w")

    # ── Separator ───────────────────────────────────────────────────────── #
    tk.Frame(win, bg="#e5e7eb", height=1).pack(fill="x", padx=20)

    # ── Scrollable task text ─────────────────────────────────────────────── #
    frame = tk.Frame(win, bg="#ffffff")
    frame.pack(fill="both", expand=True, padx=20, pady=12)

    scrollbar = tk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text_widget = tk.Text(
        frame,
        font=body_font,
        bg="#f7f8fa", fg="#1f2328",
        relief="flat", bd=0,
        wrap="word",
        width=62, height=20,
        yscrollcommand=scrollbar.set,
        padx=12, pady=10,
    )
    text_widget.insert("1.0", task)
    text_widget.config(state="disabled")
    text_widget.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=text_widget.yview)

    # ── Buttons ──────────────────────────────────────────────────────────── #
    btn_frame = tk.Frame(win, bg="#ffffff")
    btn_frame.pack(fill="x", padx=20, pady=(0, 16))

    tk.Button(
        btn_frame, text="Open IBM ICA  ->",
        font=btn_font, bg="#1d4ed8", fg="#ffffff",
        relief="flat", padx=16, pady=8, cursor="hand2",
        command=lambda: webbrowser.open(ICA_URL),
    ).pack(side="left")

    tk.Button(
        btn_frame, text="Dismiss",
        font=btn_font, bg="#f7f8fa", fg="#57606a",
        relief="flat", padx=16, pady=8, cursor="hand2",
        command=win.destroy,
    ).pack(side="left", padx=(10, 0))

    # ── Countdown label ──────────────────────────────────────────────────── #
    countdown_var = tk.StringVar()
    tk.Label(
        btn_frame, textvariable=countdown_var,
        font=tkfont.Font(family="Segoe UI", size=10),
        bg="#ffffff", fg="#57606a",
    ).pack(side="right")

    def countdown(secs_left: int) -> None:
        if not win.winfo_exists():
            return
        if secs_left <= 0:
            win.destroy()
            return
        countdown_var.set(f"Auto-closes in {secs_left}s")
        win.after(1000, countdown, secs_left - 1)

    # ── Position: bottom-right corner ────────────────────────────────────── #
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    ww = win.winfo_reqwidth()
    wh = win.winfo_reqheight()
    win.geometry(f"+{sw - ww - 24}+{sh - wh - 64}")

    win.attributes("-topmost", True)

    if NOTIFICATION_TIMEOUT > 0:
        win.after(100, countdown, NOTIFICATION_TIMEOUT)
    else:
        countdown_var.set("Click 'Dismiss' to close")

    win.mainloop()


if __name__ == "__main__":
    # Task file path is passed as the first argument
    task_file = sys.argv[1]
    with open(task_file, encoding="utf-8") as f:
        task_text = f.read()
    # Delete the temp file immediately after reading
    import os
    os.unlink(task_file)
    show_popup(task_text)
