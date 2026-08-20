# ============================================================
#  modules/attendance_manager.py
#  Mark attendance and query attendance records
# ============================================================

import datetime
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modules.database import execute_query


def mark_attendance(student_id, subject_id):
    """
    Mark a student as Present for today in the given subject.
    Prevents duplicate entries (UNIQUE KEY in DB handles it too).
    Returns True if marked, False if already marked.
    """
    today = datetime.date.today().isoformat()
    now   = datetime.datetime.now().strftime("%H:%M:%S")

    # Check if already marked today
    existing = execute_query(
        "SELECT att_id FROM attendance "
        "WHERE student_id=%s AND subject_id=%s AND date=%s",
        (student_id, subject_id, today), fetch=True
    )
    if existing:
        return False   # already marked

    execute_query(
        "INSERT INTO attendance (student_id, subject_id, date, time, status) "
        "VALUES (%s, %s, %s, %s, 'Present')",
        (student_id, subject_id, today, now)
    )
    return True


def get_attendance_report(subject_id=None, from_date=None, to_date=None, class_name=None):
    """
    Flexible attendance report query.
    Returns list of dicts with student + attendance info.
    """
    query = """
        SELECT s.name, s.roll_no, s.class,
               sub.name AS subject,
               a.date, a.time, a.status
        FROM attendance a
        JOIN students s  ON a.student_id  = s.student_id
        JOIN subjects sub ON a.subject_id = sub.subject_id
        WHERE 1=1
    """
    params = []

    if subject_id:
        query  += " AND a.subject_id = %s"
        params.append(subject_id)
    if from_date:
        query  += " AND a.date >= %s"
        params.append(from_date)
    if to_date:
        query  += " AND a.date <= %s"
        params.append(to_date)
    if class_name:
        query  += " AND s.class = %s"
        params.append(class_name)

    query += " ORDER BY a.date DESC, s.name ASC"
    return execute_query(query, params, fetch=True) or []


def get_student_percentage(student_id, subject_id):
    """Calculate attendance percentage for one student in one subject."""
    total = execute_query(
        "SELECT COUNT(*) AS cnt FROM attendance "
        "WHERE student_id=%s AND subject_id=%s",
        (student_id, subject_id), fetch=True
    )
    present = execute_query(
        "SELECT COUNT(*) AS cnt FROM attendance "
        "WHERE student_id=%s AND subject_id=%s AND status='Present'",
        (student_id, subject_id), fetch=True
    )
    t = total[0]["cnt"]   if total   else 0
    p = present[0]["cnt"] if present else 0
    return round((p / t * 100), 1) if t > 0 else 0.0


def get_all_subjects():
    return execute_query(
        "SELECT subject_id, name, code, semester FROM subjects ORDER BY name",
        fetch=True
    ) or []


def get_today_summary(subject_id):
    """How many students marked present today for a subject."""
    today = datetime.date.today().isoformat()
    result = execute_query(
        "SELECT COUNT(*) AS cnt FROM attendance "
        "WHERE subject_id=%s AND date=%s AND status='Present'",
        (subject_id, today), fetch=True
    )
    return result[0]["cnt"] if result else 0
