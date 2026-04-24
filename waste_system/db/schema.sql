CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    province TEXT,
    city TEXT,
    barangay TEXT,
    house_id TEXT UNIQUE,
    address TEXT
);

CREATE TABLE IF NOT EXISTS pickups (
    pickup_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);