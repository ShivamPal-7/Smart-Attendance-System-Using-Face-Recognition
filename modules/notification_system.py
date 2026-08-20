# ============================================================
#  modules/notification_system.py
#  Send email alerts to students with low attendance
# ============================================================

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import EMAIL_CONFIG, ATTENDANCE_THRESHOLD
from modules.database import execute_query


def get_low_attendance_students(subject_id):
    """
    Returns list of students whose attendance in subject_id < THRESHOLD.
    Each item: {student_id, name, email, roll_no, percentage}
    """
    rows = execute_query("""
        SELECT s.student_id, s.name, s.email, s.roll_no,
               ROUND(
                   COUNT(CASE WHEN a.status='Present' THEN 1 END) * 100.0 / COUNT(*),
                   1
               ) AS percentage
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE a.subject_id = %s
        GROUP BY s.student_id
        HAVING percentage < %s
        ORDER BY percentage ASC
    """, (subject_id, ATTENDANCE_THRESHOLD), fetch=True)
    return rows or []


def send_email_alert(student_email, student_name, subject_name, percentage):
    """Send a single email alert to one student."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"⚠ Low Attendance Alert — {subject_name}"
        msg["From"]    = EMAIL_CONFIG["sender_email"]
        msg["To"]      = student_email

        # Plain text version
        text = (
            f"Dear {student_name},\n\n"
            f"Your attendance in {subject_name} is {percentage}%, "
            f"which is below the required {ATTENDANCE_THRESHOLD}%.\n\n"
            f"Please attend classes regularly to avoid being barred from examinations.\n\n"
            f"Regards,\nSmart Attendance System\nDepartment of Computer Science"
        )

        # HTML version
        html = f"""
        <html><body style="font-family:Arial,sans-serif;background:#f0f4f8;padding:24px;">
          <div style="max-width:520px;margin:auto;background:#fff;border-radius:10px;
                      border:1px solid #ddd;overflow:hidden;">
            <div style="background:#1F4E79;padding:20px 24px;">
              <h2 style="color:#fff;margin:0;">⚠ Attendance Alert</h2>
            </div>
            <div style="padding:24px;">
              <p>Dear <strong>{student_name}</strong>,</p>
              <p>Your attendance in <strong>{subject_name}</strong> is currently:</p>
              <div style="text-align:center;padding:16px;background:#FAECE7;
                          border-radius:8px;margin:16px 0;">
                <span style="font-size:36px;font-weight:bold;color:#E74C3C;">
                  {percentage}%
                </span>
              </div>
              <p>The minimum required attendance is
                 <strong>{ATTENDANCE_THRESHOLD}%</strong>.
                 Please attend classes regularly to avoid being
                 <strong>barred from examinations</strong>.</p>
              <hr style="border:none;border-top:1px solid #eee;margin:16px 0;">
              <p style="color:#888;font-size:12px;">
                This is an automated message from the Smart Attendance System.<br>
                Department of Computer Science
              </p>
            </div>
          </div>
        </body></html>
        """

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html,  "html"))

        with smtplib.SMTP(EMAIL_CONFIG["smtp_host"], EMAIL_CONFIG["smtp_port"]) as server:
            server.starttls()
            server.login(EMAIL_CONFIG["sender_email"], EMAIL_CONFIG["app_password"])
            server.sendmail(EMAIL_CONFIG["sender_email"], student_email, msg.as_string())

        print(f"[EMAIL] Sent to {student_name} <{student_email}> — {percentage}%")
        return True

    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False


def send_all_alerts(subject_id, progress_callback=None):
    """
    Check all students in subject_id,
    send email to all who are below threshold.
    Returns (sent_count, failed_count, student_list)
    """
    students = get_low_attendance_students(subject_id)
    if not students:
        return 0, 0, []

    # Get subject name
    sub = execute_query(
        "SELECT name FROM subjects WHERE subject_id=%s",
        (subject_id,), fetch=True
    )
    subject_name = sub[0]["name"] if sub else "Your Subject"

    sent = 0; failed = 0
    for i, s in enumerate(students):
        if s["email"]:
            ok = send_email_alert(
                s["email"], s["name"], subject_name, s["percentage"]
            )
            if ok:
                # Log in notifications table
                execute_query(
                    "INSERT INTO notifications (student_id, message) VALUES (%s, %s)",
                    (s["student_id"],
                     f"Alert sent: {s['percentage']}% in {subject_name}")
                )
                sent += 1
            else:
                failed += 1
        if progress_callback:
            progress_callback(i + 1, len(students))

    return sent, failed, students
