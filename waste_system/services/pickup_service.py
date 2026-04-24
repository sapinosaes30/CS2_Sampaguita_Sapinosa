import sqlite3

from db.connection import get_connection
from utils.audit import log_action

STATUS_FLOW = ["Pending", "Driver Assigned", "In Transit", "Completed"]
PRIORITY_OPTIONS = ["Normal", "High", "Urgent"]
ALLOWED_SORT_FIELDS = {"pickup_id", "date", "time", "status", "priority", "created_at"}
ALLOWED_TRANSITIONS = {
    "Pending": ["Driver Assigned"],
    "Driver Assigned": ["In Transit"],
    "In Transit": ["Completed"],
    "Completed": []
}

def create_pickup(user_id, date, time, priority="Normal", notes=""):
    if priority not in PRIORITY_OPTIONS:
        return False, "Invalid priority"

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM users WHERE user_id=? AND is_deleted=0", (user_id,))
    if not cur.fetchone():
        conn.close()
        return False, "User not found"

    try:
        cur.execute("""
            INSERT INTO pickups (user_id, date, time, priority, notes, status)
            VALUES (?, ?, ?, ?, ?, 'Pending')
        """, (user_id, date, time, priority, notes))
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.close()
        return False, str(exc)
    conn.close()
    log_action("Pickup scheduled", f"user_id={user_id} date={date} time={time} priority={priority}")
    return True, "Pickup scheduled"


def get_all_pickups(search_text=None, status_filter=None, sort_by="date", ascending=True):
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = "date"
    direction = "ASC" if ascending else "DESC"
    query = """
        SELECT pickups.*, users.name AS user_name, users.city AS city
        FROM pickups
        JOIN users ON pickups.user_id = users.user_id
        WHERE pickups.is_deleted=0 AND users.is_deleted=0
    """
    params = []
    if search_text:
        query += " AND (users.name LIKE ? OR users.city LIKE ? OR pickups.notes LIKE ? OR pickups.priority LIKE ? )"
        params.extend([f"%{search_text}%"] * 4)
    if status_filter:
        query += " AND pickups.status = ?"
        params.append(status_filter)
    query += f" ORDER BY {sort_by} {direction}"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall()
    conn.close()
    return data


def get_pickups_by_month(year, month):
    month_pattern = f"{year:04d}-{month:02d}-%"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pickups.*, users.name AS user_name, users.city AS city
        FROM pickups
        JOIN users ON pickups.user_id = users.user_id
        WHERE pickups.is_deleted=0 AND users.is_deleted=0 AND pickups.date LIKE ?
        ORDER BY pickups.date, pickups.time
    """, (month_pattern,))
    data = cur.fetchall()
    conn.close()
    return data


def get_pickups_by_date(date):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT pickups.*, users.name AS user_name, users.city AS city
        FROM pickups
        JOIN users ON pickups.user_id = users.user_id
        WHERE pickups.is_deleted=0 AND users.is_deleted=0 AND pickups.date = ?
        ORDER BY pickups.time
    """, (date,))
    data = cur.fetchall()
    conn.close()
    return data


def get_pickup_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM pickups WHERE is_deleted=0")
    count = cur.fetchone()["count"]
    conn.close()
    return count


def get_pending_pickup_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM pickups WHERE is_deleted=0 AND status='Pending'")
    count = cur.fetchone()["count"]
    conn.close()
    return count


def get_high_priority_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM pickups WHERE is_deleted=0 AND priority='High'")
    count = cur.fetchone()["count"]
    conn.close()
    return count


def update_pickup_status(pickup_id, status):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status FROM pickups WHERE pickup_id=? AND is_deleted=0", (pickup_id,))
    current = cur.fetchone()
    if not current:
        conn.close()
        return False, "Pickup not found"
    current_status = current["status"]
    if status not in STATUS_FLOW:
        conn.close()
        return False, "Invalid status"
    if status == current_status:
        conn.close()
        return False, "Status is already set"
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    if status not in allowed:
        conn.close()
        return False, f"Cannot move from {current_status} to {status}"
    cur.execute("""
        UPDATE pickups
        SET status=?, updated_at=CURRENT_TIMESTAMP
        WHERE pickup_id=? AND is_deleted=0
    """, (status, pickup_id))
    conn.commit()
    conn.close()
    log_action("Pickup status updated", f"pickup_id={pickup_id} status={status}")
    return True, "Updated"


def soft_delete_pickup(pickup_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE pickups
        SET is_deleted=1, deleted_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
        WHERE pickup_id=? AND is_deleted=0
    """, (pickup_id,))
    conn.commit()
    conn.close()
    log_action("Pickup deleted", f"pickup_id={pickup_id}")
    return True, "Deleted"