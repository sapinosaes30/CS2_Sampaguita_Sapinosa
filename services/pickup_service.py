from db.connection import get_connection


VALID_STATUS = ["Pending", "Driver Assigned", "Completed"]

def create_pickup(user_id, date, time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO pickups (user_id, date, time, status)
        VALUES (?, ?, ?, 'Pending')
    """, (user_id, date, time))

    conn.commit()
    conn.close()

    return True, "Pickup scheduled"


def get_all_pickups():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM pickups ORDER BY pickup_id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


def update_pickup_status(pickup_id, status):
    if status not in VALID_STATUS:
        return False, "Invalid status"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE pickups
        SET status = ?
        WHERE pickup_id = ?
    """, (status, pickup_id))

    conn.commit()
    conn.close()

    return True, "Pickup status updated"


def delete_pickup(pickup_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM pickups WHERE pickup_id = ?", (pickup_id,))

    conn.commit()
    conn.close()

    return True, "Pickup deleted"