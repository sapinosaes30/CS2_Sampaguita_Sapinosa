from db.connection import get_connection

def create_user(name, province, city, barangay, house_id, address):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users (name, province, city, barangay, house_id, address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, province, city, barangay, house_id, address))
    conn.commit()
    conn.close()
    return True, "User created"

def get_all_users():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY user_id DESC")
    data = cur.fetchall()
    conn.close()
    return data

def update_user(user_id, name, province, city, barangay, house_id, address):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users
        SET name=?, province=?, city=?, barangay=?, house_id=?, address=?
        WHERE user_id=?
    """, (name, province, city, barangay, house_id, address, user_id))
    conn.commit()
    conn.close()
    return True, "Updated"

def delete_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    return True, "Deleted"