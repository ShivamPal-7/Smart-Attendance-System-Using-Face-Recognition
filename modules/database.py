# ============================================================
#  modules/database.py  —  MySQL connection helper
# ============================================================

import mysql.connector
from mysql.connector import Error
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_CONFIG


def get_connection():
    """Return a live MySQL connection."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"[DB ERROR] Cannot connect to MySQL: {e}")
        return None


def execute_query(query, params=None, fetch=False):
    """
    Run any SQL query.
    fetch=True  → returns list of rows
    fetch=False → returns lastrowid (for INSERT) or rowcount
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
            return cursor.lastrowid
    except Error as e:
        print(f"[QUERY ERROR] {e}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def test_connection():
    conn = get_connection()
    if conn:
        print("[OK] Database connected successfully!")
        conn.close()
        return True
    return False


if __name__ == "__main__":
    print("Testing database connection...")
    test_connection()