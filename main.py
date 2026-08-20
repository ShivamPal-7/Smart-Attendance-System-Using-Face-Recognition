#!/usr/bin/env python3
# ============================================================
#  main.py  —  Smart Attendance System Entry Point
#
#  Run:  python main.py
# ============================================================

import tkinter as tk
import sys, os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.database    import test_connection
from ui.login_window     import LoginWindow
from ui.dashboard        import Dashboard


def launch():
    # ── Test DB connection first ──────────────────────────
    if not test_connection():
        import tkinter.messagebox as mb
        root = tk.Tk(); root.withdraw()
        mb.showerror(
            "Database Error",
            "Cannot connect to MySQL!\n\n"
            "1. Make sure XAMPP is running\n"
            "2. Check config.py — DB_CONFIG settings\n"
            "3. Import database.sql into phpMyAdmin"
        )
        root.destroy()
        return

    root = tk.Tk()
    root.withdraw()   # hide until login succeeds

    def on_login_success(faculty):
        root.deiconify()
        for w in root.winfo_children():
            w.destroy()
        Dashboard(root, faculty)

    login_win = tk.Toplevel(root)
    login_win.protocol("WM_DELETE_WINDOW", root.destroy)
    LoginWindow(login_win, on_success=on_login_success)

    root.mainloop()


if __name__ == "__main__":
    launch()
