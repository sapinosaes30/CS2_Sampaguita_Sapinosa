from db.connection import get_connection

STATUS_FLOW = ["Pending", "Driver Assigned", "In Transit", "Completed"]

def create_pickup(user_id, date, time):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO pickups (user_id, date, time, status)
        VALUES (?, ?, ?, 'Pending')
    """, (user_id, date, time))
    conn.commit()
    conn.close()
    return True, "Pickup scheduled"

def get_all_pickups():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pickups ORDER BY date ASC")
    data = cur.fetchall()
    conn.close()
    return data

def update_pickup_status(pickup_id, status):
    if status not in STATUS_FLOW:
        return False, "Invalid status"
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE pickups
        SET status=?
        WHERE pickup_id=?
    """, (status, pickup_id))
    conn.commit()
    conn.close()
    return True, "Updated"