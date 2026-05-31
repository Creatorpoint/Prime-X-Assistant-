import sqlite3

db = sqlite3.connect(
    "primex.db",
    check_same_thread=False
)

cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
user_id INTEGER PRIMARY KEY,
name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups(
group_id INTEGER PRIMARY KEY,
title TEXT
)
""")

db.commit()


def add_user(user_id, name):
    cursor.execute(
        "INSERT OR IGNORE INTO users VALUES (?,?)",
        (user_id, name)
    )
    db.commit()


def add_group(group_id, title):
    cursor.execute(
        "INSERT OR IGNORE INTO groups VALUES (?,?)",
        (group_id, title)
    )
    db.commit()


def get_users():
    return cursor.execute(
        "SELECT user_id FROM users"
    ).fetchall()


def get_groups():
    return cursor.execute(
        "SELECT group_id FROM groups"
    ).fetchall()


def total_users():
    return cursor.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]


def total_groups():
    return cursor.execute(
        "SELECT COUNT(*) FROM groups"
    ).fetchone()[0]

def all_users():
    return cursor.execute(
        "SELECT user_id FROM users"
    ).fetchall()


def all_groups():
    return cursor.execute(
        "SELECT group_id FROM groups"
    ).fetchall()
