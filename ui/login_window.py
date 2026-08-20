# ============================================================
#  ui/login_window.py  —  Login screen
# ============================================================

import tkinter as tk
from tkinter import messagebox
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.database import execute_query


def verify_login(email, password):
    result = execute_query(
        "SELECT faculty_id, name FROM faculty WHERE email=%s AND password=%s",
        (email, password),
        fetch=True
    )
    return result[0] if result else None


class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success

        self.root.title("Smart Attendance System — Login")
        self.root.geometry("430x620")
        self.root.resizable(False, False)
        self.root.configure(bg="#0D1B2A")

        self.show_password = False

        self._build()

    def toggle_password(self):
        self.show_password = not self.show_password

        if self.show_password:
            self.pass_entry.config(show="")
            self.show_btn.config(text="🙈 Hide")
        else:
            self.pass_entry.config(show="•")
            self.show_btn.config(text="👁 Show")

    def _build(self):

        # ---------------- Header ----------------

        tk.Label(
            self.root,
            text="🎓",
            font=("Arial", 48),
            bg="#0D1B2A",
            fg="#00B4D8"
        ).pack(pady=(35, 5))

        tk.Label(
            self.root,
            text="Smart Attendance System",
            font=("Segoe UI", 20, "bold"),
            bg="#0D1B2A",
            fg="white"
        ).pack()

        tk.Label(
            self.root,
            text="Face Recognition Based",
            font=("Segoe UI", 11),
            bg="#0D1B2A",
            fg="#00B4D8"
        ).pack(pady=(5, 25))

        # ---------------- Card ----------------

        card = tk.Frame(self.root, bg="#1A2A3A")
        card.pack(padx=30, fill="x")

        # Email

        tk.Label(
            card,
            text="Email Address",
            font=("Segoe UI", 10),
            bg="#1A2A3A",
            fg="#94A3B8"
        ).pack(anchor="w", padx=20, pady=(20, 5))

        self.email_var = tk.StringVar()

        email_entry = tk.Entry(
            card,
            textvariable=self.email_var,
            font=("Segoe UI", 12),
            bg="#0D1B2A",
            fg="white",
            insertbackground="white",
            bd=0
        )

        email_entry.pack(fill="x", padx=20, ipady=10)
        email_entry.focus()

        tk.Frame(card, bg="#2E86DE", height=2).pack(fill="x", padx=20)

        # Password

        tk.Label(
            card,
            text="Password",
            font=("Segoe UI", 10),
            bg="#1A2A3A",
            fg="#94A3B8"
        ).pack(anchor="w", padx=20, pady=(20, 5))

        self.pass_var = tk.StringVar()

        pass_frame = tk.Frame(card, bg="#1A2A3A")
        pass_frame.pack(fill="x", padx=20)

        self.pass_entry = tk.Entry(
            pass_frame,
            textvariable=self.pass_var,
            show="•",
            font=("Segoe UI", 12),
            bg="#0D1B2A",
            fg="white",
            insertbackground="white",
            bd=0
        )

        self.pass_entry.pack(side="left", fill="x", expand=True, ipady=10)

        self.show_btn = tk.Button(
            pass_frame,
            text="👁 Show",
            command=self.toggle_password,
            bg="#1A2A3A",
            fg="white",
            relief="flat",
            cursor="hand2"
        )

        self.show_btn.pack(side="right", padx=5)

        tk.Frame(card, bg="#2E86DE", height=2).pack(fill="x", padx=20)

        tk.Frame(card, bg="#1A2A3A", height=25).pack()

        # ---------------- Login Button ----------------

        tk.Button(
            self.root,
            text="LOGIN",
            font=("Segoe UI", 13, "bold"),
            bg="#2E86DE",
            fg="white",
            activebackground="#1A73E8",
            relief="flat",
            cursor="hand2",
            command=self._login
        ).pack(fill="x", padx=30, pady=25, ipady=12)

        # ---------------- Footer ----------------

        tk.Label(
            self.root,
            text="Enter your registered email and password",
            font=("Segoe UI", 9),
            bg="#0D1B2A",
            fg="#94A3B8"
        ).pack()

        tk.Label(
            self.root,
            text="Developed by Shivam Pal",
            font=("Segoe UI", 9, "italic"),
            bg="#0D1B2A",
            fg="#64748B"
        ).pack(pady=(15, 10))

        self.root.bind("<Return>", lambda e: self._login())

    def _login(self):

        email = self.email_var.get().strip()
        password = self.pass_var.get().strip()

        if not email or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your email and password."
            )
            return

        faculty = verify_login(email, password)

        if faculty:
            self.on_success(faculty)
        else:
            messagebox.showerror(
                "Login Failed",
                "Incorrect email or password."
            )