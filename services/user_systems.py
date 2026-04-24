from db.connection import get_connection

# CREATE
def create_user(name, province, city, barangay, house_id, address):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (name, province, city, barangay, house_id, address)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, province, city, barangay, house_id, address))

    conn.commit()
    conn.close()

    return True, "User created successfully"


# READ ALL
def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users ORDER BY user_id DESC")
    rows = cursor.fetchall()

    conn.close()
    return rows


# READ ONE
def get_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    conn.close()
    return row


# UPDATE
def update_user(user_id, name, province, city, barangay, house_id, address):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET name=?, province=?, city=?, barangay=?, house_id=?, address=?
        WHERE user_id=?
    """, (name, province, city, barangay, house_id, address, user_id))

    conn.commit()
    conn.close()

    return True, "User updated successfully"


# DELETE
def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))

    conn.commit()
    conn.close()

    return True, "User deleted"
