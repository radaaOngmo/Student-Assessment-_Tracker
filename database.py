"""SQLite database setup and data-access functions.

Demo accounts created on first run:
Admin: admin / Admin123!
User: student / Student123!
Change demo passwords before using real personal data.
"""
import sqlite3
import hashlib
import hmac
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "student_assessment_tracker.db"

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def hash_password(password, salt=None):
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000).hex()
    return salt, digest

def verify_password(password, salt, expected_hash):
    _, actual = hash_password(password, salt)
    return hmac.compare_digest(actual, expected_hash)

def initialize_database():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            full_name TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','user')),
            active INTEGER NOT NULL DEFAULT 1,
            profile_picture TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            task_name TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Pending',
            due_date TEXT DEFAULT '',
            date_added TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );
        """)
        # Backward-compatible migration for databases created before profile settings.
        user_columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "profile_picture" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT DEFAULT ''")
        for username, full_name, password, role in [
            ("admin", "System Administrator", "Admin123!", "admin"),
            ("student", "Demo Student", "Student123!", "user")
        ]:
            if not conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
                salt, digest = hash_password(password)
                conn.execute(
                    "INSERT INTO users(username,full_name,password_salt,password_hash,role) VALUES(?,?,?,?,?)",
                    (username, full_name, salt, digest, role)
                )

def authenticate(username, password):
    with connect() as conn:
        row = conn.execute("SELECT * FROM users WHERE username=? AND active=1", (username.strip(),)).fetchone()
        if row and verify_password(password, row["password_salt"], row["password_hash"]):
            return dict(row)
    return None

def get_tasks(user):
    with connect() as conn:
        if user["role"] == "admin":
            rows = conn.execute("""
                SELECT tasks.*, users.full_name AS owner_name
                FROM tasks JOIN users USING(user_id) ORDER BY tasks.task_id DESC
            """).fetchall()
        else:
            rows = conn.execute("SELECT tasks.*, '' AS owner_name FROM tasks WHERE user_id=? ORDER BY task_id DESC",
                                (user["user_id"],)).fetchall()
        return [dict(r) for r in rows]

def save_task(user, task_id, name, description, priority, status, due_date, owner_id=None):
    name = name.strip()
    if not name:
        raise ValueError("Please enter a task title.")
    with connect() as conn:
        if task_id:
            if user["role"] == "admin":
                result = conn.execute("""UPDATE tasks SET task_name=?,description=?,priority=?,status=?,due_date=?
                    WHERE task_id=?""", (name, description.strip(), priority, status, due_date.strip(), task_id))
            else:
                result = conn.execute("""UPDATE tasks SET task_name=?,description=?,priority=?,status=?,due_date=?
                    WHERE task_id=? AND user_id=?""",
                    (name, description.strip(), priority, status, due_date.strip(), task_id, user["user_id"]))
            if result.rowcount == 0:
                raise PermissionError("This task cannot be edited from your account.")
        else:
            target = owner_id if user["role"] == "admin" and owner_id else user["user_id"]
            conn.execute("""INSERT INTO tasks(user_id,task_name,description,priority,status,due_date)
                VALUES(?,?,?,?,?,?)""", (target, name, description.strip(), priority, status, due_date.strip()))

def delete_task(user, task_id):
    with connect() as conn:
        if user["role"] == "admin":
            result = conn.execute("DELETE FROM tasks WHERE task_id=?", (task_id,))
        else:
            result = conn.execute("DELETE FROM tasks WHERE task_id=? AND user_id=?", (task_id, user["user_id"]))
        if result.rowcount == 0:
            raise PermissionError("This task cannot be deleted from your account.")

def update_profile(user_id, full_name, profile_picture=None):
    full_name = full_name.strip()
    if not full_name:
        raise ValueError("Please enter your full name.")
    with connect() as conn:
        if profile_picture is None:
            result = conn.execute("UPDATE users SET full_name=? WHERE user_id=?", (full_name, user_id))
        else:
            result = conn.execute("UPDATE users SET full_name=?, profile_picture=? WHERE user_id=?",
                                  (full_name, profile_picture, user_id))
        if result.rowcount == 0:
            raise ValueError("The account could not be found.")
        row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
        return dict(row)


def change_password(user_id, current_password, new_password):
    if len(new_password) < 8:
        raise ValueError("Your new password must contain at least 8 characters.")
    with connect() as conn:
        row = conn.execute("SELECT password_salt,password_hash FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row or not verify_password(current_password, row["password_salt"], row["password_hash"]):
            raise ValueError("Your current password is incorrect.")
        salt, digest = hash_password(new_password)
        conn.execute("UPDATE users SET password_salt=?,password_hash=? WHERE user_id=?",
                     (salt, digest, user_id))


def list_users():
    with connect() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT user_id,username,full_name,role,active,profile_picture,created_at FROM users ORDER BY user_id"
        ).fetchall()]

def create_user(username, full_name, password, role="user"):
    if not username.strip() or not full_name.strip() or len(password) < 8:
        raise ValueError("Enter a username, full name, and password of at least 8 characters.")
    if role not in ("admin", "user"):
        raise ValueError("Invalid role.")
    salt, digest = hash_password(password)
    with connect() as conn:
        try:
            conn.execute("INSERT INTO users(username,full_name,password_salt,password_hash,role) VALUES(?,?,?,?,?)",
                         (username.strip(), full_name.strip(), salt, digest, role))
        except sqlite3.IntegrityError:
            raise ValueError("That username already exists.")

def toggle_user(user_id):
    with connect() as conn:
        row = conn.execute("SELECT active,role FROM users WHERE user_id=?", (user_id,)).fetchone()
        if not row:
            raise ValueError("User not found.")
        if row["role"] == "admin":
            raise ValueError("Admin accounts cannot be disabled from this screen.")
        conn.execute("UPDATE users SET active=? WHERE user_id=?", (0 if row["active"] else 1, user_id))

def dashboard_stats(user):
    tasks = get_tasks(user)
    return {
        "total": len(tasks),
        "pending": sum(t["status"] == "Pending" for t in tasks),
        "progress": sum(t["status"] == "In Progress" for t in tasks),
        "completed": sum(t["status"] == "Completed" for t in tasks),
        "users": len(list_users()) if user["role"] == "admin" else None
    }
