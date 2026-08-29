import sqlite3
from datetime import datetime

DB_NAME = "foodbridge.db"

def init_db():
    """Run this once at app startup to create the table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT NOT NULL,
            quantity TEXT NOT NULL,
            food_type TEXT NOT NULL,
            location TEXT NOT NULL,
            donor_name TEXT NOT NULL,
            donor_contact TEXT,
            cooked_time TEXT,
            expiry_time TEXT NOT NULL,
            status TEXT DEFAULT 'Available',
            claimed_by TEXT,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def add_listing(food_name, quantity, food_type, location, donor_name,
                 donor_contact, cooked_time, expiry_time):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO listings
        (food_name, quantity, food_type, location, donor_name,
         donor_contact, cooked_time, expiry_time, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Available', ?)
    """, (food_name, quantity, food_type, location, donor_name,
          donor_contact, cooked_time, expiry_time,
          datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_all_listings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def claim_listing(listing_id, claimed_by):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE listings SET status = 'Claimed', claimed_by = ?
        WHERE id = ?
    """, (claimed_by, listing_id))
    conn.commit()
    conn.close()

def confirm_pickup(listing_id):
    # Make sure the listings table exists
    init_db()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE listings
        SET status = 'Picked Up'
        WHERE id = ? AND status = 'Claimed'
    """, (listing_id,))

    conn.commit()
    conn.close()

def delete_listing(listing_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    conn.commit()
    conn.close()

def update_expired_listings():
    """Call this before displaying listings — auto-marks expired ones."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        UPDATE listings SET status = 'Expired'
        WHERE expiry_time < ? AND status = 'Available'
    """, (now,))
    conn.commit()
    conn.close()

def get_listings_by_donor(donor_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM listings WHERE donor_name = ? ORDER BY created_at DESC", (donor_name,))
    rows = cursor.fetchall()
    conn.close()
    return rows
# ---------------------------------------------------------
# USER ACCOUNTS
# ---------------------------------------------------------
import hashlib
import hmac
import os


def init_users_table():
    conn = sqlite3.connect("foodbridge.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return f"{salt}${password_hash}"


def create_user(username, password):
    username = username.strip()

    if len(username) < 3:
        return False, "Username must contain at least 3 characters."

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    try:
        conn = sqlite3.connect("foodbridge.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, hash_password(password))
        )

        conn.commit()
        conn.close()

        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        return False, "This username already exists."


def authenticate_user(username, password):
    conn = sqlite3.connect("foodbridge.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ? COLLATE NOCASE",
        (username.strip(),)
    )

    user = cursor.fetchone()
    conn.close()

    if user is None:
        return False

    salt, saved_hash = user[0].split("$")
    entered_hash = hash_password(password, salt).split("$")[1]

    return hmac.compare_digest(saved_hash, entered_hash)
# ---------------------------------------------------------
# NGO PROFILES
# ---------------------------------------------------------
def init_ngos_table():
    conn = sqlite3.connect("foodbridge.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ngos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ngo_name TEXT NOT NULL,
            contact_person TEXT NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_ngo(ngo_name, contact_person, phone, location, description):
    conn = sqlite3.connect("foodbridge.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO ngos (
            ngo_name,
            contact_person,
            phone,
            location,
            description
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        ngo_name,
        contact_person,
        phone,
        location,
        description
    ))

    conn.commit()
    conn.close()


def get_all_ngos():
    conn = sqlite3.connect("foodbridge.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM ngos
        ORDER BY created_at DESC
    """)

    ngos = cursor.fetchall()
    conn.close()

    return ngos
# ---------------------------------------------------------
# MAP LOCATIONS
# ---------------------------------------------------------
def init_map_locations_table():
    conn = sqlite3.connect("foodbridge.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS map_locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            place_name TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            location_type TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def add_map_location(
    place_name,
    address,
    latitude,
    longitude,
    location_type
):
    conn = sqlite3.connect("foodbridge.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO map_locations (
            place_name,
            address,
            latitude,
            longitude,
            location_type
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        place_name,
        address,
        latitude,
        longitude,
        location_type
    ))

    conn.commit()
    conn.close()


def get_map_locations():
    conn = sqlite3.connect("foodbridge.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM map_locations
        ORDER BY created_at DESC
    """)

    locations = cursor.fetchall()
    conn.close()

    return locations
