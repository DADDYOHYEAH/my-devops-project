"""
Database module for DevOps Flix
Handles SQLite database operations for users and watchlist persistence.
"""
import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

# Get database path from environment variable with fallback
DB_PATH = os.environ.get("DB_PATH", "devopsflix.db")


def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_db():
    """Initialize the database with required tables."""
    logger.info(f"Initializing database at: {DB_PATH}")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Watchlist table with user_id foreign key
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            movie_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            poster_path TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            UNIQUE(user_id, movie_id)
        )
    ''')
    
    # Seed default admin user if not exists
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            ("admin", "admin@devopsflix.com", "123")
        )
        logger.info("Default admin user created")
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")


# ============================================================
# USER OPERATIONS
# ============================================================

def get_user(username):
    """Get user by username. Returns dict or None."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "id": row["id"],
            "username": row["username"],
            "email": row["email"],
            "password": row["password"]
        }
    return None


def create_user(username, email, password):
    """Create a new user. Returns user_id or None if failed."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, password)
        )
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        logger.info(f"USER CREATED: {username} (ID: {user_id})")
        return user_id
    except sqlite3.IntegrityError:
        logger.warning(f"USER CREATE FAILED: Username '{username}' already exists")
        return None


def check_user_exists(username):
    """Check if username already exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


# ============================================================
# WATCHLIST OPERATIONS
# ============================================================

def add_to_watchlist(user_id, movie_id, title, poster_path):
    """Add movie to user's watchlist. Returns True if successful."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO watchlist (user_id, movie_id, title, poster_path) VALUES (?, ?, ?, ?)",
            (user_id, movie_id, title, poster_path)
        )
        conn.commit()
        conn.close()
        logger.info(f"WATCHLIST ADD: Movie '{title}' added for user_id {user_id}")
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"WATCHLIST ADD FAILED: Movie already in watchlist")
        return False


def remove_from_watchlist(user_id, movie_id):
    """Remove movie from user's watchlist. Returns True if movie was removed."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?",
        (user_id, movie_id)
    )
    removed = cursor.rowcount > 0
    conn.commit()
    conn.close()
    
    if removed:
        logger.info(f"WATCHLIST REMOVE: Movie {movie_id} removed for user_id {user_id}")
    return removed


def get_user_watchlist(user_id):
    """Get all movies in user's watchlist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT movie_id, title, poster_path FROM watchlist WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    return [
        {
            "id": row["movie_id"],
            "title": row["title"],
            "poster_path": row["poster_path"]
        }
        for row in rows
    ]


def is_in_watchlist(user_id, movie_id):
    """Check if movie is already in user's watchlist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM watchlist WHERE user_id = ? AND movie_id = ?",
        (user_id, movie_id)
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists
