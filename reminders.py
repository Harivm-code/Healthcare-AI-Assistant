
import sqlite3
import hashlib
import secrets
import hmac

DB_NAME = "healthcare.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


# =====================================
# DATABASE INITIALIZATION
# =====================================

def init_db():

    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            reminder_date TEXT NOT NULL,
            reminder_time TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    columns = [
        row[1] for row in
        conn.execute("PRAGMA table_info(reminders)").fetchall()
    ]

    if "user_id" not in columns:
        conn.execute(
            "ALTER TABLE reminders ADD COLUMN user_id INTEGER"
        )

    if "status" not in columns:
        conn.execute(
            "ALTER TABLE reminders ADD COLUMN status TEXT DEFAULT 'Pending'"
        )

    user_columns = [
        row[1] for row in
        conn.execute("PRAGMA table_info(users)").fetchall()
    ]

    if "created_at" not in user_columns:
        conn.execute(
            "ALTER TABLE users ADD COLUMN created_at TEXT"
        )

        conn.execute("""
            UPDATE users
            SET created_at = CURRENT_TIMESTAMP
            WHERE created_at IS NULL
        """)

    conn.commit()
    conn.close()


# =====================================
# PASSWORD SECURITY
# =====================================

def hash_password(password, salt):

    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200000
    ).hex()


# =====================================
# USER REGISTRATION
# =====================================

def register_user(username, password):

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO users
            (username, password_hash, salt, created_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (username, password_hash, salt)
        )

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()


# =====================================
# USER LOGIN
# =====================================

def login_user(username, password):

    conn = get_connection()

    user = conn.execute(
        """
        SELECT id, password_hash, salt
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()

    conn.close()

    if user is None:
        return None

    user_id, stored_hash, salt = user

    entered_hash = hash_password(password, salt)

    if hmac.compare_digest(entered_hash, stored_hash):
        return user_id

    return None


# =====================================
# USER PROFILE
# =====================================

def get_user_profile(user_id):

    conn = get_connection()

    profile = conn.execute(
        """
        SELECT id, username, created_at
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    conn.close()

    return profile


def update_username(user_id, new_username):

    new_username = new_username.strip()

    if not new_username:
        return False, "Username cannot be empty."

    conn = get_connection()

    try:

        conn.execute(
            """
            UPDATE users
            SET username = ?
            WHERE id = ?
            """,
            (new_username, user_id)
        )

        conn.commit()

        return True, "Username updated successfully."

    except sqlite3.IntegrityError:

        return False, "That username is already taken."

    finally:
        conn.close()


def change_password(user_id, current_password, new_password):

    if len(new_password) < 8:
        return False, "New password must contain at least 8 characters."

    conn = get_connection()

    user = conn.execute(
        """
        SELECT password_hash, salt
        FROM users
        WHERE id = ?
        """,
        (user_id,)
    ).fetchone()

    if user is None:
        conn.close()
        return False, "Account not found."

    stored_hash, old_salt = user

    entered_hash = hash_password(current_password, old_salt)

    if not hmac.compare_digest(entered_hash, stored_hash):
        conn.close()
        return False, "Current password is incorrect."

    new_salt = secrets.token_hex(16)
    new_hash = hash_password(new_password, new_salt)

    conn.execute(
        """
        UPDATE users
        SET password_hash = ?, salt = ?
        WHERE id = ?
        """,
        (new_hash, new_salt, user_id)
    )

    conn.commit()
    conn.close()

    return True, "Password changed successfully."


# =====================================
# ADD REMINDER
# =====================================

def add_reminder(user_id, title, reminder_date, reminder_time):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO reminders
        (user_id, title, reminder_date, reminder_time, status)
        VALUES (?, ?, ?, ?, 'Pending')
        """,
        (
            user_id,
            title,
            str(reminder_date),
            str(reminder_time)
        )
    )

    conn.commit()
    conn.close()


# =====================================
# GET REMINDERS
# =====================================

# Original function retained for Dashboard compatibility

def get_reminders(user_id):

    conn = get_connection()

    reminders = conn.execute(
        """
        SELECT id, title, reminder_date, reminder_time
        FROM reminders
        WHERE user_id = ?
        ORDER BY reminder_date, reminder_time
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    return reminders


# New function includes reminder status

def get_reminders_with_status(user_id):

    conn = get_connection()

    reminders = conn.execute(
        """
        SELECT id, title, reminder_date, reminder_time, status
        FROM reminders
        WHERE user_id = ?
        ORDER BY reminder_date, reminder_time
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    return reminders


# =====================================
# COMPLETE REMINDER
# =====================================

def complete_reminder(reminder_id, user_id):

    conn = get_connection()

    cursor = conn.execute(
        """
        UPDATE reminders
        SET status = 'Completed'
        WHERE id = ? AND user_id = ?
        """,
        (reminder_id, user_id)
    )

    conn.commit()

    updated = cursor.rowcount > 0

    conn.close()

    return updated


# =====================================
# DELETE REMINDER
# =====================================

def delete_reminder(reminder_id, user_id):

    conn = get_connection()

    conn.execute(
        """
        DELETE FROM reminders
        WHERE id = ? AND user_id = ?
        """,
        (reminder_id, user_id)
    )

    conn.commit()
    conn.close()


# =====================================
# INITIALIZE DATABASE
# =====================================

init_db()
