"""
DevOps Flix - Security Test Suite
Pytest tests for password hashing, backward compatibility, and cookie security
"""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import (
    init_db, execute_query, hash_password, check_password,
    get_user, create_user
)
import app


@pytest.fixture(autouse=True)
def setup_database():
    """Initialize database before each test"""
    init_db()
    yield
    # Cleanup happens automatically since tests use isolated transactions


class TestPasswordSecurity:
    """Test password hashing and backward compatibility"""
    
    def test_new_user_password_is_hashed(self):
        """Test that new users get bcrypt-hashed passwords"""
        # Clean up if user exists
        execute_query("DELETE FROM users WHERE username = ?", ("testuser_new",))
        
        # Create new user
        user_id = create_user("testuser_new", "test@example.com", "SecurePass123")
        
        assert user_id is not None, "User creation should succeed"
        
        # Verify password is hashed
        user = get_user("testuser_new")
        assert user is not None
        assert user['password'].startswith('$2b$'), "Password should be bcrypt-hashed"
        assert len(user['password']) > 50, "Hashed password should be long"
        assert user['password'] != "SecurePass123", "Password should not be plain text"
        
        # Cleanup
        execute_query("DELETE FROM users WHERE username = ?", ("testuser_new",))
    
    def test_new_user_login_with_correct_password(self):
        """Test that login works with correct hashed password"""
        # Clean up if user exists
        execute_query("DELETE FROM users WHERE username = ?", ("testuser_login",))
        
        # Create new user
        create_user("testuser_login", "login@example.com", "MyPassword456")
        
        # Test login with correct password
        assert check_password("testuser_login", "MyPassword456") == True
        
        # Cleanup
        execute_query("DELETE FROM users WHERE username = ?", ("testuser_login",))
    
    def test_new_user_login_rejects_wrong_password(self):
        """Test that login fails with incorrect password"""
        # Clean up if user exists
        execute_query("DELETE FROM users WHERE username = ?", ("testuser_wrong",))
        
        # Create new user
        create_user("testuser_wrong", "wrong@example.com", "CorrectPass789")
        
        # Test login with wrong password
        assert check_password("testuser_wrong", "WrongPassword") == False
        assert check_password("testuser_wrong", "incorrectpass789") == False
        assert check_password("testuser_wrong", "") == False
        
        # Cleanup
        execute_query("DELETE FROM users WHERE username = ?", ("testuser_wrong",))
    
    def test_legacy_user_plain_text_login_works(self):
        """Test that legacy users with plain text passwords can still log in"""
        # Clean up if user exists
        execute_query("DELETE FROM users WHERE username = ?", ("olduser",))
        
        # Simulate old user with plain text password (pre-security update)
        execute_query(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            ("olduser", "old@example.com", "plaintext123")
        )
        
        # Verify password is plain text
        user = get_user("olduser")
        assert user['password'] == "plaintext123", "Initial password should be plain text"
        
        # Test login (should work with backward compatibility)
        assert check_password("olduser", "plaintext123") == True
        
        # Cleanup
        execute_query("DELETE FROM users WHERE username = ?", ("olduser",))
    
    def test_legacy_user_password_auto_upgrade(self):
        """Test that plain text passwords are automatically upgraded to hashed on login"""
        # Clean up if user exists
        execute_query("DELETE FROM users WHERE username = ?", ("upgradeuser",))
        
        # Create legacy user with plain text password
        execute_query(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            ("upgradeuser", "upgrade@example.com", "oldpassword")
        )
        
        # Verify initial state (plain text)
        user_before = get_user("upgradeuser")
        assert user_before['password'] == "oldpassword"
        
        # Login (should trigger auto-upgrade)
        login_success = check_password("upgradeuser", "oldpassword")
        assert login_success == True
        
        # Verify password was upgraded to hash
        user_after = get_user("upgradeuser")
        assert user_after['password'].startswith('$2b$'), "Password should be upgraded to bcrypt hash"
        assert user_after['password'] != "oldpassword", "Password should no longer be plain text"
        
        # Verify login still works with the same password after upgrade
        assert check_password("upgradeuser", "oldpassword") == True
        
        # Cleanup
        execute_query("DELETE FROM users WHERE username = ?", ("upgradeuser",))
    
    def test_nonexistent_user_login_fails(self):
        """Test that login fails for users that don't exist"""
        assert check_password("nonexistentuser123", "anypassword") == False


class TestCookieSecurity:
    """Test secure cookie configuration"""
    
    def test_cookie_httponly_enabled(self):
        """Test that HttpOnly flag is enabled (prevents XSS attacks)"""
        assert app.app.config['SESSION_COOKIE_HTTPONLY'] == True
    
    def test_cookie_samesite_protection(self):
        """Test that SameSite protection is configured (prevents CSRF)"""
        assert app.app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
    
    def test_cookie_secure_adapts_to_environment(self):
        """Test that HTTPS-only cookies are enabled in production, disabled locally"""
        # The value should match IS_PRODUCTION detection
        expected_secure = bool(app.IS_PRODUCTION)
        assert app.app.config['SESSION_COOKIE_SECURE'] == expected_secure
    
    def test_session_timeout_configured(self):
        """Test that session timeout is set (security best practice)"""
        assert app.app.config['PERMANENT_SESSION_LIFETIME'] == 3600  # 1 hour


class TestPasswordHashingUtilities:
    """Test password hashing utility functions"""
    
    def test_hash_password_produces_bcrypt_hash(self):
        """Test that hash_password function produces valid bcrypt hashes"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert hashed.startswith('$2b$'), "Should produce bcrypt hash"
        assert len(hashed) > 50, "Bcrypt hash should be long"
        assert hashed != password, "Hash should be different from plain text"
    
    def test_hash_password_produces_unique_hashes(self):
        """Test that same password produces different hashes (salted)"""
        password = "SamePassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Due to salt, same password should produce different hashes
        assert hash1 != hash2, "Same password should produce different hashes (salt)"
        assert hash1.startswith('$2b$')
        assert hash2.startswith('$2b$')
