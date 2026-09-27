"""
backend/auth.py
---------------
Simple file-based user auth backend using JSON + bcrypt hashing.
Stores users in users_db.json next to this file.
"""
import json, os, hashlib, secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "users_db.json")


def _load_db():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "r") as f:
        return json.load(f)


def _save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


def _hash_password(password: str, salt: str) -> str:
    return hashlib.sha256((password + salt).encode()).hexdigest()


def register_user(name: str, email: str, phone: str, password: str, city: str) -> dict:
    db = _load_db()
    email = email.strip().lower()
    if email in db:
        return {"success": False, "message": "Email already registered. Please log in."}
    salt = secrets.token_hex(16)
    db[email] = {
        "name": name.strip(),
        "email": email,
        "phone": phone.strip(),
        "city": city,
        "password_hash": _hash_password(password, salt),
        "salt": salt,
        "created_at": datetime.now().isoformat(),
        "emergency_contacts": [],
    }
    _save_db(db)
    return {"success": True, "message": "Account created successfully!", "user": db[email]}


def login_user(email: str, password: str) -> dict:
    db = _load_db()
    email = email.strip().lower()
    if email not in db:
        return {"success": False, "message": "Email not found. Please sign up first."}
    user = db[email]
    if _hash_password(password, user["salt"]) != user["password_hash"]:
        return {"success": False, "message": "Incorrect password. Please try again."}
    safe_user = {k: v for k, v in user.items() if k not in ("password_hash", "salt")}
    return {"success": True, "message": f"Welcome back, {user['name']}!", "user": safe_user}


def get_user(email: str) -> dict | None:
    db = _load_db()
    return db.get(email.strip().lower())


def update_emergency_contacts(email: str, contacts: list) -> bool:
    db = _load_db()
    email = email.strip().lower()
    if email not in db:
        return False
    db[email]["emergency_contacts"] = contacts
    _save_db(db)
    return True
