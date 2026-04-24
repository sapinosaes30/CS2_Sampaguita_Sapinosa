import sqlite3

from db.connection import get_connection
from utils.audit import log_action

ALLOWED_SORT_FIELDS = {"user_id", "name", "city", "barangay", "created_at"}

def create_user(name, province, city, barangay, house_id, address):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (name, province, city, barangay, house_id, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, province, city, barangay, house_id, address))
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.close()
        return False, str(exc)
    conn.close()
    log_action("User created", f"{name} | {house_id}")
    return True, "User created"


def get_all_users(search_text=None, city_filter=None, sort_by="user_id", ascending=False):
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = "user_id"
    direction = "ASC" if ascending else "DESC"
    query = "SELECT * FROM users WHERE is_deleted=0"
    params = []
    if search_text:
        query += " AND (name LIKE ? OR house_id LIKE ? OR address LIKE ?)"
        params.extend([f"%{search_text}%"] * 3)
    if city_filter:
        query += " AND city = ?"
        params.append(city_filter)
    query += f" ORDER BY {sort_by} {direction}"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    data = cur.fetchall()
    conn.close()
    return data


def get_user_by_id(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE user_id=? AND is_deleted=0", (user_id,))
    user = cur.fetchone()
    conn.close()
    return user


def get_active_user_options():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id, name FROM users WHERE is_deleted=0 ORDER BY name")
    options = [(row["user_id"], row["name"]) for row in cur.fetchall()]
    conn.close()
    return options


def get_cities():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT city FROM users WHERE is_deleted=0 ORDER BY city")
    cities = [row["city"] for row in cur.fetchall() if row["city"]]
    conn.close()
    return cities


def get_user_count():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS count FROM users WHERE is_deleted=0")
    count = cur.fetchone()["count"]
    conn.close()
    return count


def update_user(user_id, name, province, city, barangay, house_id, address):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE users
            SET name=?, province=?, city=?, barangay=?, house_id=?, address=?, updated_at=CURRENT_TIMESTAMP
            WHERE user_id=? AND is_deleted=0
        """, (name, province, city, barangay, house_id, address, user_id))
        conn.commit()
    except sqlite3.IntegrityError as exc:
        conn.close()
        return False, str(exc)
    conn.close()
    log_action("User updated", f"user_id={user_id} | {name}")
    return True, "Updated"


def soft_delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET is_deleted=1, deleted_at=CURRENT_TIMESTAMP, updated_at=CURRENT_TIMESTAMP
        WHERE user_id=? AND is_deleted=0
    """, (user_id,))
    conn.commit()
    conn.close()
    log_action("User deleted", f"user_id={user_id}")
    return True, "Deleted"