"""
Database module for DevOps Flix
Supports dual-mode operation:
- Local mode: SQLite (when DB_HOST not set)
- Production mode: PostgreSQL (when DB_HOST is set)
"""

# done by ageelan
import os
import logging
import bcrypt

logger = logging.getLogger(__name__)

# Database configuration from environment variables
DB_HOST = os.environ.get("DB_HOST")  # If set, use PostgreSQL
DB_USER = os.environ.get("DB_USER", "devopsflix")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "devopsflix123")
DB_NAME = os.environ.get("DB_NAME", "devopsflix")
DB_PATH = os.environ.get("DB_PATH", "devopsflix.db")  # SQLite path

# Determine database mode
USE_POSTGRES = DB_HOST is not None

if USE_POSTGRES:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    logger.info(f"Database Mode: PostgreSQL (Host: {DB_HOST})")
else:
    import sqlite3
    logger.info(f"Database Mode: SQLite (Path: {DB_PATH})")


def get_db_connection():
    """Create and return a database connection based on environment."""
    if USE_POSTGRES:
        conn = psycopg2.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursor_factory=RealDictCursor
        )
        return conn
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn


def execute_query(query, params=None, fetch=None):
    """
    Execute a database query with automatic placeholder conversion.
    Args:
        query: SQL query string (use ? for placeholders) (sql command)
        params: Tuple of parameters ( the actual data)
        fetch: 'one', 'all', or None (for INSERT/UPDATE/DELETE)
    Returns:
        Result of fetch operation or lastrowid/rowcount
    """
    # Convert SQLite placeholders (?) to PostgreSQL placeholders (%s)
    if USE_POSTGRES and params:
        query = query.replace("?", "%s")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = None
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        elif fetch is None:
            # For INSERT/UPDATE/DELETE
            conn.commit()
            if USE_POSTGRES:
                result = cursor.rowcount
            else:
                result = cursor.lastrowid or cursor.rowcount
        
        conn.close()
        return result
    
    except Exception as e:
        conn.close()
        logger.error(f"Database error: {e}")
        raise


def init_db():
    """Initialize the database with required tables."""
    logger.info("Initializing database...")
    
    # SQL compatible with both SQLite and PostgreSQL
    if USE_POSTGRES:
        users_table = '''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        watchlist_table = '''
            CREATE TABLE IF NOT EXISTS watchlist (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                movie_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                poster_path TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                UNIQUE(user_id, movie_id)
            )
        '''
    else:
        users_table = '''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        watchlist_table = '''
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
        '''
    
    execute_query(users_table)
    execute_query(watchlist_table)
    
    # Seed default admin user if not exists
    admin_exists = execute_query(
        "SELECT id FROM users WHERE username = ?",
        ("admin",),
        fetch='one'
    )
    
    if not admin_exists:
        execute_query(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            ("admin", "admin@devopsflix.com", "123")
        )
        logger.info("Default admin user created")
    
    logger.info("Database initialized successfully")


# ============================================================
# PASSWORD SECURITY FUNCTIONS
# ============================================================

def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt)
    return password_hash.decode('utf-8')


def check_password(username, password):
    """
    Verify password with backward compatibility.
    Supports both hashed (new) and plain text (legacy) passwords.
    Auto-upgrades plain text passwords to hashed on successful login.
    
    Returns:
        bool: True if password is correct, False otherwise
    """
    user = get_user(username)
    if not user:
        return False
    
    stored_password = user['password']
    
    # Check if it's a bcrypt hash (new users)
    if stored_password.startswith(('$2b$', '$2a$', '$2y$')):
        try:
            # Verify hashed password
            return bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
        except (ValueError, AttributeError) as e:
            # Malformed hash, fail safely
            logger.error(f"Invalid hash format for user {username}: {e}")
            return False
    
    # Legacy plain text password (old users)
    if stored_password == password:
        # Auto-upgrade to hashed password
        logger.info(f"Auto-upgrading password for user: {username}")
        new_hash = hash_password(password)
        upgrade_user_password(username, new_hash)
        return True
    
    return False


def upgrade_user_password(username, password_hash):
    """Upgrade a user's password to a hashed version."""
    execute_query(
        "UPDATE users SET password = ? WHERE username = ?",
        (password_hash, username)
    )
    logger.info(f"Password upgraded for user: {username}")


# ============================================================
# USER OPERATIONS
# ============================================================

def get_user(username):
    """Get user by username. Returns dict or None."""
    row = execute_query(
        "SELECT * FROM users WHERE username = ?",
        (username,),
        fetch='one'
    )
    
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
        # Hash password before storing
        password_hash = hash_password(password)
        
        if USE_POSTGRES:
            # PostgreSQL: Use RETURNING to get the new ID
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id",
                (username, email, password_hash)
            )
            user_id = cursor.fetchone()['id']
            conn.commit()
            conn.close()
        else:
            # SQLite: Use lastrowid
            user_id = execute_query(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
        
        logger.info(f"USER CREATED: {username} (ID: {user_id}, password hashed)")
        return user_id
    
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            logger.warning(f"USER CREATE FAILED: Username '{username}' already exists")
            return None
        raise


def check_user_exists(username):
    """Check if username already exists."""
    result = execute_query(
        "SELECT id FROM users WHERE username = ?",
        (username,),
        fetch='one'
    )
    return result is not None


# ============================================================
# WATCHLIST OPERATIONS
# ============================================================

def add_to_watchlist(user_id, movie_id, title, poster_path):
    """Add movie to user's watchlist. Returns True if successful."""
    try:
        execute_query(
            "INSERT INTO watchlist (user_id, movie_id, title, poster_path) VALUES (?, ?, ?, ?)",
            (user_id, movie_id, title, poster_path)
        )
        logger.info(f"WATCHLIST ADD: Movie '{title}' added for user_id {user_id}")
        return True
    except Exception as e:
        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            logger.warning(f"WATCHLIST ADD FAILED: Movie already in watchlist")
            return False
        raise


def remove_from_watchlist(user_id, movie_id):
    """Remove movie from user's watchlist. Returns True if movie was removed."""
    rowcount = execute_query(
        "DELETE FROM watchlist WHERE user_id = ? AND movie_id = ?",
        (user_id, movie_id)
    )
    
    removed = rowcount > 0
    if removed:
        logger.info(f"WATCHLIST REMOVE: Movie {movie_id} removed for user_id {user_id}")
    return removed


def get_user_watchlist(user_id):
    """Get all movies in user's watchlist."""
    rows = execute_query(
        "SELECT movie_id, title, poster_path FROM watchlist WHERE user_id = ? ORDER BY added_at DESC",
        (user_id,),
        fetch='all'
    )
    
    return [
        {
            "id": row["movie_id"],
            "title": row["title"],
            "poster_path": row["poster_path"]
        }
        for row in (rows or [])
    ]


def is_in_watchlist(user_id, movie_id):
    """Check if movie is already in user's watchlist."""
    result = execute_query(
        "SELECT id FROM watchlist WHERE user_id = ? AND movie_id = ?",
        (user_id, movie_id),
        fetch='one'
    )
    return result is not None
