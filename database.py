"""
Prime X Assistant — Database Module
SQLite-based persistent storage for users, groups, strikes, and moderation logs.
"""

import sqlite3
import threading
from datetime import datetime, timedelta

DB_PATH = "prime_x.db"

# Thread-local storage for connections (thread-safe)
_local = threading.local()


def get_connection() -> sqlite3.Connection:
    """Return a thread-local SQLite connection."""
    if not hasattr(_local, "conn") or _local.conn is None:
        _local.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _local.conn.row_factory = sqlite3.Row
    return _local.conn


def init_db():
    """Initialize all database tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id     INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL DEFAULT 'User',
            join_date   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Groups table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS groups (
            chat_id     INTEGER PRIMARY KEY,
            name        TEXT    NOT NULL DEFAULT 'Group',
            join_date   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    # Strikes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strikes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            chat_id     INTEGER NOT NULL,
            count       INTEGER NOT NULL DEFAULT 0,
            last_strike TEXT    NOT NULL DEFAULT (datetime('now')),
            UNIQUE(user_id, chat_id)
        )
    """)

    # Moderation logs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS mod_logs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            chat_id     INTEGER NOT NULL,
            content     TEXT    NOT NULL,
            strike      INTEGER NOT NULL,
            timestamp   TEXT    NOT NULL DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    print("✅ Database tables ready.")


# ═══════════════════════════════════════════════════════════════════════════
# USER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def add_user(user_id: int, name: str):
    """Add a user if not already in DB."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)",
            (user_id, name)
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] add_user error: {e}")


def get_user_count() -> int:
    """Return total registered users."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) FROM users").fetchone()
        return row[0] if row else 0
    except Exception:
        return 0


def get_all_users() -> list[int]:
    """Return all user IDs."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT user_id FROM users").fetchall()
        return [r[0] for r in rows]
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════
# GROUP FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def add_group(chat_id: int, name: str):
    """Add a group if not already in DB."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO groups (chat_id, name) VALUES (?, ?)",
            (chat_id, name)
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] add_group error: {e}")


def get_group_count() -> int:
    """Return total registered groups."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) FROM groups").fetchone()
        return row[0] if row else 0
    except Exception:
        return 0


def get_all_groups() -> list[int]:
    """Return all group chat IDs."""
    conn = get_connection()
    try:
        rows = conn.execute("SELECT chat_id FROM groups").fetchall()
        return [r[0] for r in rows]
    except Exception:
        return []


# ═══════════════════════════════════════════════════════════════════════════
# STRIKE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def add_strike(user_id: int, chat_id: int) -> int:
    """
    Add a strike for user in the given chat.
    Returns new total strike count.
    """
    conn = get_connection()
    try:
        now = datetime.now().isoformat()

        # Upsert
        conn.execute("""
            INSERT INTO strikes (user_id, chat_id, count, last_strike)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(user_id, chat_id)
            DO UPDATE SET
                count = count + 1,
                last_strike = excluded.last_strike
        """, (user_id, chat_id, now))
        conn.commit()

        row = conn.execute(
            "SELECT count FROM strikes WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        ).fetchone()
        return row[0] if row else 1
    except Exception as e:
        print(f"[DB] add_strike error: {e}")
        return 1


def get_strikes(user_id: int, chat_id: int) -> int:
    """Return current strike count for a user in a chat."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT count FROM strikes WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        ).fetchone()
        return row[0] if row else 0
    except Exception:
        return 0


def reset_strikes(user_id: int, chat_id: int):
    """Reset strikes for a user in a chat."""
    conn = get_connection()
    try:
        conn.execute(
            "DELETE FROM strikes WHERE user_id = ? AND chat_id = ?",
            (user_id, chat_id)
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] reset_strikes error: {e}")


def reset_old_strikes():
    """Reset strikes older than 30 days (called periodically)."""
    conn = get_connection()
    try:
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        conn.execute(
            "DELETE FROM strikes WHERE last_strike < ?",
            (cutoff,)
        )
        conn.commit()
        print("[DB] Old strikes cleaned up.")
    except Exception as e:
        print(f"[DB] reset_old_strikes error: {e}")


def get_total_strikes() -> int:
    """Return total strike count across all chats."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT SUM(count) FROM strikes").fetchone()
        return row[0] or 0
    except Exception:
        return 0


# ═══════════════════════════════════════════════════════════════════════════
# MODERATION LOGS
# ═══════════════════════════════════════════════════════════════════════════

def log_moderation(user_id: int, chat_id: int, content: str, strike: int):
    """Log a moderation action."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO mod_logs (user_id, chat_id, content, strike) VALUES (?, ?, ?, ?)",
            (user_id, chat_id, content, strike)
        )
        conn.commit()
    except Exception as e:
        print(f"[DB] log_moderation error: {e}")


def get_moderation_logs(chat_id: int, limit: int = 10) -> list:
    """Return recent moderation logs for a chat."""
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT user_id, content, strike, timestamp
            FROM mod_logs
            WHERE chat_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (chat_id, limit)
        ).fetchall()
        return [(r[0], r[1], r[2], r[3]) for r in rows]
    except Exception:
        return []
