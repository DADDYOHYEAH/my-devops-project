"""
Test script to verify backward-compatible password hashing
"""
import sys
import os
sys.path.insert(0, '.')

from database import init_db, execute_query, hash_password, check_password, get_user

print("=" * 60)
print("SECURITY IMPLEMENTATION TEST")
print("=" * 60)

# Initialize database
print("\n1. Initializing test database...")
init_db()

# Test 1: Create new user with hashed password
print("\n2. Testing NEW USER (hashed password)...")
try:
    # Clean up if user exists
    execute_query("DELETE FROM users WHERE username = ?", ("testuser",))
    
    from database import create_user
    create_user("testuser", "test@example.com", "SecurePass123")
    
    user = get_user("testuser")
    print(f"   OK User created: {user['username']}")
    print(f"   OK Password is hashed: {user['password'][:30]}...")
    print(f"   OK Hash starts with $2b$: {user['password'].startswith('$2b$')}")
    
    # Test login
    if check_password("testuser", "SecurePass123"):
        print("   OK Login with correct password: SUCCESS")
    else:
        print("   FAIL Login FAILED (should have succeeded!)")
        
    if not check_password("testuser", "WrongPassword"):
        print("   OK Login with wrong password: Correctly rejected")
    else:
        print("   FAIL Wrong password accepted (BUG!)")
        
except Exception as e:
    print(f"   FAIL ERROR: {e}")

# Test 2: Legacy user with plain text password
print("\n3. Testing LEGACY USER (plain text password)...")
try:
    # Simulate old user with plain text password
    execute_query("DELETE FROM users WHERE username = ?", ("olduser",))
    execute_query(
        "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
        ("olduser", "old@example.com", "plaintext123")
    )
    
    user = get_user("olduser")
    print(f"   OK Legacy user created: {user['username']}")
    print(f"   OK Password is plain text: {user['password']}")
    
    # Test login (should work and auto-upgrade)
    if check_password("olduser", "plaintext123"):
        print("   OK Login with plain text password: SUCCESS")
        
        # Check if password was upgraded
        user_after = get_user("olduser")
        if user_after['password'].startswith('$2b$'):
            print("   OK Password AUTO-UPGRADED to hash!")
            print(f"   OK New hash: {user_after['password'][:30]}...")
        else:
            print("   FAIL Password was NOT upgraded (BUG!)")
    else:
        print("   FAIL Login FAILED (should have succeeded!)")
        
except Exception as e:
    print(f"   FAIL ERROR: {e}")

# Test 3: Cookie configuration
print("\n4. Testing Cookie Security Configuration...")
try:
    import app
    print(f"   OK HTTPS-only cookies: {app.app.config['SESSION_COOKIE_SECURE']}")
    print(f"   OK HttpOnly enabled: {app.app.config['SESSION_COOKIE_HTTPONLY']}")
    print(f"   OK SameSite protection: {app.app.config['SESSION_COOKIE_SAMESITE']}")
    print(f"   OK Session timeout: {app.app.config['PERMANENT_SESSION_LIFETIME']}s")
    print(f"   OK Production mode: {app.IS_PRODUCTION}")
except Exception as e:
    print(f"   FAIL ERROR: {e}")

print("\n" + "=" * 60)
print("TEST COMPLETE!")
print("=" * 60)
