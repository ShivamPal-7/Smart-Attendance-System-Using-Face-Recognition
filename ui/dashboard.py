# ============================================================
#  ui/dashboard.py  —  Main Dashboard (Tabs: Attendance,
#                       Register, Students, Reports, Alerts)
# ============================================================

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading, os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.register_student   import register_student, get_all_students, delete_student
from modules.train_model        import train_model
from modules.recognize_face     import start_recognition
from modules.attendance_manager import (get_all_subjects, get_attendance_report,
                                        get_today_summary)
from modules.report_generator   import generate_excel_report
from modules.notification_system import send_all_alerts, get_low_attendance_students


# ── Color palette ─────────────────────────────────────────────
BG      = "#0D1B2A"
CARD    = "#1A2A3A"
ACCENT  = "#2E86DE"
TEAL    = "#00B4D8"
GREEN   = "#27AE60"
RED     = "#E74C3C"
ORANGE  = "#E67E22"
WHITE   = "#FFFFFF"
GRAY    = "#94A3B8"


def label(parent, text, **kw):
    return tk.Label(parent, text=text, bg=kw.pop("bg", CARD),
                    fg=kw.pop("fg", WHITE), **kw)


def btn(parent, text, command, color=ACCENT, **kw):
    return tk.Button(parent, text=text, command=command,
                     bg=color, fg=WHITE, font=("Arial", 10, "bold"),
                     relief="flat", cursor="hand2",
                     activebackground="#1A5276",
                     padx=12, pady=6, **kw)


def entry_row(parent, lbl, row, default=""):
    label(parent, lbl, fg=GRAY, font=("Arial", 9)).grid(
        row=row, column=0, sticky="w", padx=8, pady=2)
    var = tk.StringVar(value=default)
    e   = tk.Entry(parent, textvariable=var, font=("Arial", 10),
                   bg="#0D1B2A", fg=WHITE, insertbackground=WHITE,
                   relief="flat", bd=0)
    e.grid(row=row, column=1, sticky="ew", padx=8, pady=2, ipady=5)
    tk.Frame(parent, bg=ACCENT, height=1).grid(
        row=row+1, column=1, sticky="ew", padx=8)
    return var


class Dashboard:
    def __init__(self, root, faculty):
        self.root    = root
        self.faculty = faculty
        self.root.title(f"Smart Attendance — {faculty['name']}")
        self.root.geometry("960x620")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self._stop_event = threading.Event()
        self._build()

    # ══════════════════════════════════════════════════════════
    def _build(self):
        # ── Top bar ──────────────────────────────────────────
        top = tk.Frame(self.root, bg="#0A1628", height=52)
        top.pack(fill="x")
        tk.Label(top, text="  🎓 Smart Attendance System",
                 font=("Arial", 14, "bold"), bg="#0A1628", fg=WHITE).pack(side="left", pady=12)
        tk.Label(top, text=f"Logged in: {self.faculty['name']}  |  ",
                 font=("Arial", 10), bg="#0A1628", fg=GRAY).pack(side="right", pady=16)

        # ── Notebook tabs ────────────────────────────────────
        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook",       background=BG, borderwidth=0)
        style.configure("TNotebook.Tab",   background=CARD, foreground=GRAY,
                        padding=[16, 8],   font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", ACCENT)],
                  foreground=[("selected", WHITE)])

        nb = ttk.Notebook(self.root)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self.tab_attendance = tk.Frame(nb, bg=BG)
        self.tab_register   = tk.Frame(nb, bg=BG)
        self.tab_students   = tk.Frame(nb, bg=BG)
        self.tab_reports    = tk.Frame(nb, bg=BG)
        self.tab_alerts     = tk.Frame(nb, bg=BG)

        nb.add(self.tab_attendance, text="📷  Mark Attendance")
        nb.add(self.tab_register,   text="➕  Register Student")
        nb.add(self.tab_students,   text="👥  All Students")
        nb.add(self.tab_reports,    text="📊  Reports")
        nb.add(self.tab_alerts,     text="📧  Email Alerts")

        self._build_attendance_tab()
        self._build_register_tab()
        self._build_students_tab()
        self._build_reports_tab()
        self._build_alerts_tab()

    # ══════════════════════════════════════════════════════════
    #  TAB 1 — MARK ATTENDANCE
    # ══════════════════════════════════════════════════════════
    def _build_attendance_tab(self):
        f = self.tab_attendance
        label(f, "📷  Mark Attendance Using Face Recognition",
              bg=BG, fg=TEAL, font=("Arial", 14, "bold")).pack(pady=(20, 4))
        label(f, "Select a subject, then click START — the webcam will open automatically.",
              bg=BG, fg=GRAY, font=("Arial", 10)).pack()

        card = tk.Frame(f, bg=CARD, padx=24, pady=20)
        card.pack(padx=40, pady=16, fill="x")
        card.columnconfigure(1, weight=1)

        label(card, "Select Subject:", fg=GRAY, font=("Arial", 10)).grid(
            row=0, column=0, sticky="w", padx=8, pady=8)

        subjects = get_all_subjects()
        sub_names = [f"{s['name']} ({s['code']})" for s in subjects]
        self._subjects = subjects

        self.sub_var = tk.StringVar()
        cb = ttk.Combobox(card, textvariable=self.sub_var,
                          values=sub_names, state="readonly",
                          font=("Arial", 10), width=36)
        cb.grid(row=0, column=1, padx=8, pady=8, sticky="w")
        if sub_names:
            cb.current(0)

        # Marked list
        label(card, "Marked Today:", fg=GRAY, font=("Arial", 10)).grid(
            row=1, column=0, sticky="nw", padx=8, pady=8)
        self.marked_box = tk.Listbox(card, bg="#0D1B2A", fg=GREEN,
                                     font=("Courier", 10), height=8,
                                     selectbackground=ACCENT, bd=0,
                                     highlightthickness=0)
        self.marked_box.grid(row=1, column=1, padx=8, pady=8, sticky="ew")

        self.att_status = label(card, "Status: Idle", fg=GRAY, font=("Arial", 10))
        self.att_status.grid(row=2, column=0, columnspan=2, pady=4)

        btn_frame = tk.Frame(f, bg=BG)
        btn_frame.pack(pady=8)
        btn(btn_frame, "▶  START Recognition", self._start_attendance,
            color=GREEN).pack(side="left", padx=8)
        btn(btn_frame, "⬛  STOP", self._stop_attendance,
            color=RED).pack(side="left", padx=8)
        btn(btn_frame, "🔧  Train / Retrain Model", self._train,
            color=ORANGE).pack(side="left", padx=8)

    def _get_selected_subject_id(self):
        idx = [f"{s['name']} ({s['code']})" for s in self._subjects].index(self.sub_var.get()) \
              if self.sub_var.get() else -1
        return self._subjects[idx]["subject_id"] if idx >= 0 else None

    def _start_attendance(self):
        sub_id = self._get_selected_subject_id()
        if not sub_id:
            messagebox.showwarning("Select Subject", "Please select a subject first.")
            return
        self._stop_event.clear()
        self.att_status.config(text="Status: Recognition running...", fg=GREEN)

        def on_recognized(name, roll_no, sid):
            self.marked_box.insert(tk.END, f"✓  {name}  ({roll_no})")
            self.marked_box.yview_moveto(1.0)

        def run():
            start_recognition(sub_id, on_recognized=on_recognized,
                              stop_event=self._stop_event)
            self.att_status.config(text="Status: Session ended.", fg=GRAY)

        threading.Thread(target=run, daemon=True).start()

    def _stop_attendance(self):
        self._stop_event.set()
        self.att_status.config(text="Status: Stopped.", fg=ORANGE)

    def _train(self):
        self.att_status.config(text="Status: Training model...", fg=TEAL)
        def run():
            ok, msg = train_model()
            self.att_status.config(text=f"Status: {msg}", fg=GREEN if ok else RED)
            messagebox.showinfo("Training", msg)
        threading.Thread(target=run, daemon=True).start()

    # ══════════════════════════════════════════════════════════
    #  TAB 2 — REGISTER STUDENT
    # ══════════════════════════════════════════════════════════
    def _build_register_tab(self):
        f = self.tab_register
        label(f, "➕  Register New Student",
              bg=BG, fg=TEAL, font=("Arial", 14, "bold")).pack(pady=(20, 4))
        label(f, "Fill in all details, then click Register. Webcam will open to capture face.",
              bg=BG, fg=GRAY, font=("Arial", 10)).pack()

        card = tk.Frame(f, bg=CARD, padx=30, pady=24)
        card.pack(padx=80, pady=16)
        card.columnconfigure(1, weight=1)

        self.reg_name    = entry_row(card, "Full Name *",    0)
        self.reg_roll    = entry_row(card, "Roll Number *",  2)
        self.reg_class   = entry_row(card, "Class / Batch *",4, "CS-IV")
        self.reg_email   = entry_row(card, "Email Address",  6)
        self.reg_phone   = entry_row(card, "Phone Number",   8)

        self.reg_progress = ttk.Progressbar(card, length=360, maximum=100)
        self.reg_progress.grid(row=10, column=0, columnspan=2, pady=12, padx=8)

        self.reg_status = label(card, "", fg=GRAY, font=("Arial", 10))
        self.reg_status.grid(row=11, column=0, columnspan=2)

        btn_row = tk.Frame(card, bg=CARD)
        btn_row.grid(row=12, column=0, columnspan=2, pady=12)
        btn(btn_row, "📸  Register Student", self._register,
            color=GREEN).pack(side="left", padx=8)
        btn(btn_row, "🔧  Train Model After",
            lambda: train_model(), color=ORANGE).pack(side="left", padx=8)

    def _register(self):
        name     = self.reg_name.get().strip()
        roll     = self.reg_roll.get().strip()
        cls      = self.reg_class.get().strip()
        email    = self.reg_email.get().strip()
        phone    = self.reg_phone.get().strip()

        if not name or not roll or not cls:
            messagebox.showwarning("Missing Fields", "Name, Roll No and Class are required.")
            return

        self.reg_status.config(text="Capturing face samples...", fg=TEAL)
        self.reg_progress["value"] = 0

        def progress(n):
            self.reg_progress["value"] = n
            self.reg_status.config(text=f"Captured {n}/100 samples")

        def run():
            ok, msg = register_student(name, roll, cls, email, phone,
                                       progress_callback=progress)
            color = GREEN if ok else RED
            self.reg_status.config(text=msg, fg=color)
            messagebox.showinfo("Registration", msg)
            if ok:
                self._refresh_students()

        threading.Thread(target=run, daemon=True).start()

    # ══════════════════════════════════════════════════════════
    #  TAB 3 — ALL STUDENTS
    # ══════════════════════════════════════════════════════════
    def _build_students_tab(self):
        f = self.tab_students
        top = tk.Frame(f, bg=BG)
        top.pack(fill="x", padx=20, pady=(16, 8))
        label(top, "👥  Registered Students",
              bg=BG, fg=TEAL, font=("Arial", 14, "bold")).pack(side="left")
        btn(top, "🔄 Refresh", self._refresh_students, color=ACCENT).pack(side="right")
        btn(top, "🗑 Delete Selected",
            self._delete_student, color=RED).pack(side="right", padx=8)

        cols = ("ID", "Name", "Roll No", "Class", "Email", "Registered")
        self.student_tree = ttk.Treeview(f, columns=cols, show="headings", height=18)
        widths = [50, 180, 100, 100, 200, 140]
        for col, w in zip(cols, widths):
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=w, anchor="center")

        style = ttk.Style()
        style.configure("Treeview", background=CARD, foreground=WHITE,
                        fieldbackground=CARD, rowheight=28)
        style.configure("Treeview.Heading", background=ACCENT,
                        foreground=WHITE, font=("Arial", 10, "bold"))

        sb = ttk.Scrollbar(f, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscroll=sb.set)
        self.student_tree.pack(side="left", fill="both", expand=True, padx=(20, 0))
        sb.pack(side="left", fill="y", pady=0, padx=(0, 20))
        self._refresh_students()

    def _refresh_students(self):
        for row in self.student_tree.get_children():
            self.student_tree.delete(row)
        for s in get_all_students():
            self.student_tree.insert("", "end", values=(
                s["student_id"], s["name"], s["roll_no"],
                s["class"], s["email"] or "—",
                str(s["registered_on"])[:16]
            ))

    def _delete_student(self):
        sel = self.student_tree.selection()
        if not sel:
            messagebox.showwarning("Select", "Please select a student to delete.")
            return
        sid = self.student_tree.item(sel[0])["values"][0]
        if messagebox.askyesno("Confirm", f"Delete student ID {sid}? This cannot be undone."):
            delete_student(sid)
            self._refresh_students()

    # ══════════════════════════════════════════════════════════
    #  TAB 4 — REPORTS
    # ══════════════════════════════════════════════════════════
    def _build_reports_tab(self):
        f = self.tab_reports
        label(f, "📊  Attendance Reports",
              bg=BG, fg=TEAL, font=("Arial", 14, "bold")).pack(pady=(16, 4))

        filt = tk.Frame(f, bg=CARD, padx=16, pady=12)
        filt.pack(padx=20, fill="x")

        label(filt, "Subject:", fg=GRAY, bg=CARD).grid(row=0, column=0, padx=8)
        subjects  = get_all_subjects()
        sub_names = ["All Subjects"] + [f"{s['name']} ({s['code']})" for s in subjects]
        self._rep_subjects = subjects
        self.rep_sub = tk.StringVar(value="All Subjects")
        ttk.Combobox(filt, textvariable=self.rep_sub, values=sub_names,
                     state="readonly", width=28).grid(row=0, column=1, padx=8)

        label(filt, "From:", fg=GRAY, bg=CARD).grid(row=0, column=2, padx=8)
        self.rep_from = tk.StringVar()
        tk.Entry(filt, textvariable=self.rep_from, width=12,
                 bg="#0D1B2A", fg=WHITE, insertbackground=WHITE,
                 relief="flat").grid(row=0, column=3, padx=8)
        label(filt, "To:", fg=GRAY, bg=CARD).grid(row=0, column=4, padx=8)
        self.rep_to = tk.StringVar()
        tk.Entry(filt, textvariable=self.rep_to, width=12,
                 bg="#0D1B2A", fg=WHITE, insertbackground=WHITE,
                 relief="flat").grid(row=0, column=5, padx=8)
        label(filt, "(YYYY-MM-DD)", fg=GRAY, bg=CARD, font=("Arial", 8)).grid(
            row=1, column=3, columnspan=3, sticky="w", padx=8)

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(pady=8)
        btn(btn_row, "🔍 Load Report",  self._load_report,   color=ACCENT).pack(side="left", padx=8)
        btn(btn_row, "💾 Export Excel", self._export_excel,  color=GREEN).pack(side="left", padx=8)

        cols = ("Name", "Roll No", "Class", "Subject", "Date", "Time", "Status")
        self.rep_tree = ttk.Treeview(f, columns=cols, show="headings", height=14)
        widths        = [150, 90, 90, 150, 100, 80, 80]
        for col, w in zip(cols, widths):
            self.rep_tree.heading(col, text=col)
            self.rep_tree.column(col, width=w, anchor="center")
        self.rep_tree.tag_configure("present", foreground="#27AE60")
        self.rep_tree.tag_configure("absent",  foreground="#E74C3C")

        sb2 = ttk.Scrollbar(f, orient="vertical", command=self.rep_tree.yview)
        self.rep_tree.configure(yscroll=sb2.set)
        self.rep_tree.pack(side="left", fill="both", expand=True, padx=(20, 0))
        sb2.pack(side="left", fill="y", padx=(0, 20))

    def _load_report(self):
        sub_id = None
        if self.rep_sub.get() != "All Subjects":
            idx    = [f"{s['name']} ({s['code']})" for s in self._rep_subjects].index(self.rep_sub.get())
            sub_id = self._rep_subjects[idx]["subject_id"]

        rows = get_attendance_report(
            subject_id=sub_id or None,
            from_date=self.rep_from.get() or None,
            to_date=self.rep_to.get() or None
        )
        for row in self.rep_tree.get_children():
            self.rep_tree.delete(row)
        for r in rows:
            tag = "present" if r["status"] == "Present" else "absent"
            self.rep_tree.insert("", "end", tags=(tag,), values=(
                r["name"], r["roll_no"], r["class"], r["subject"],
                str(r["date"]), str(r["time"])[:8], r["status"]
            ))

    def _export_excel(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")],
            title="Save Attendance Report"
        )
        if not path:
            return
        ok, msg = generate_excel_report(save_path=path)
        if ok:
            messagebox.showinfo("Exported", f"Report saved:\n{path}")
        else:
            messagebox.showerror("Error", msg)

    # ══════════════════════════════════════════════════════════
    #  TAB 5 — EMAIL ALERTS
    # ══════════════════════════════════════════════════════════
    def _build_alerts_tab(self):
        f = self.tab_alerts
        label(f, "📧  Email Alerts — Low Attendance",
              bg=BG, fg=TEAL, font=("Arial", 14, "bold")).pack(pady=(16, 4))
        label(f, f"Students below {75}% attendance will receive an automatic email alert.",
              bg=BG, fg=GRAY, font=("Arial", 10)).pack()

        card = tk.Frame(f, bg=CARD, padx=16, pady=12)
        card.pack(padx=20, fill="x", pady=8)

        label(card, "Subject:", fg=GRAY, bg=CARD).grid(row=0, column=0, padx=8)
        subjects  = get_all_subjects()
        sub_names = [f"{s['name']} ({s['code']})" for s in subjects]
        self._alert_subjects = subjects
        self.alert_sub = tk.StringVar()
        cb = ttk.Combobox(card, textvariable=self.alert_sub,
                          values=sub_names, state="readonly", width=30)
        cb.grid(row=0, column=1, padx=8)
        if sub_names:
            cb.current(0)

        btn_row = tk.Frame(f, bg=BG)
        btn_row.pack(pady=8)
        btn(btn_row, "📋 Check Low Attendance", self._check_low,   color=ACCENT).pack(side="left", padx=8)
        btn(btn_row, "📧 Send All Alerts",      self._send_alerts, color=RED).pack(side="left", padx=8)

        cols = ("Name", "Roll No", "Email", "Attendance %")
        self.alert_tree = ttk.Treeview(f, columns=cols, show="headings", height=12)
        for col in cols:
            self.alert_tree.heading(col, text=col)
            self.alert_tree.column(col, width=200, anchor="center")
        self.alert_tree.pack(fill="both", expand=True, padx=20)

        self.alert_status = label(f, "", bg=BG, fg=GRAY, font=("Arial", 10))
        self.alert_status.pack(pady=4)

    def _get_alert_subject_id(self):
        if not self.alert_sub.get():
            return None
        idx = [f"{s['name']} ({s['code']})" for s in self._alert_subjects].index(self.alert_sub.get())
        return self._alert_subjects[idx]["subject_id"]

    def _check_low(self):
        sub_id = self._get_alert_subject_id()
        if not sub_id:
            return
        rows = get_low_attendance_students(sub_id)
        for row in self.alert_tree.get_children():
            self.alert_tree.delete(row)
        for r in rows:
            self.alert_tree.insert("", "end", values=(
                r["name"], r["roll_no"], r["email"] or "—", f"{r['percentage']}%"
            ))
        self.alert_status.config(text=f"{len(rows)} student(s) below 75%.", fg=ORANGE)

    def _send_alerts(self):
        sub_id = self._get_alert_subject_id()
        if not sub_id:
            return
        if not messagebox.askyesno("Confirm", "Send email alerts to all listed students?"):
            return
        self.alert_status.config(text="Sending emails...", fg=TEAL)

        def run():
            sent, failed, _ = send_all_alerts(sub_id)
            self.alert_status.config(
                text=f"Done! {sent} sent, {failed} failed.", fg=GREEN
            )
            messagebox.showinfo("Alerts Sent", f"{sent} email(s) sent successfully.")

        threading.Thread(target=run, daemon=True).start()
