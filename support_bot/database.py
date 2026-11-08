import sqlite3

def init_db(db_name):
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT,
            text TEXT NOT NULL,
            category TEXT NOT NULL,
            assigned_to TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_request(user_id, username, text, category):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO requests (user_id, username, text, category) VALUES (?, ?, ?, ?)",
        (user_id, username, text, category)
    )
    req_id = cur.lastrowid
    conn.commit()
    conn.close()
    return req_id

def get_new_requests():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM requests WHERE status = 'new'")
    rows = cur.fetchall()
    conn.close()
    return rows

def update_request_status(req_id, status, assigned_to=None):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    if assigned_to:
        cur.execute("UPDATE requests SET status = ?, assigned_to = ? WHERE id = ?", (status, assigned_to, req_id))
    else:
        cur.execute("UPDATE requests SET status = ? WHERE id = ?", (status, req_id))
    conn.commit()
    conn.close()
