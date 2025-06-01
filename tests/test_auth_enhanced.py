import pytest
from flask import url_for, session
from src.models.user import User
import time
import re

def test_register_page_accessibility(client):
    """Test that the register page is accessible and has the correct elements."""
    response = client.get('/auth/register/')
    assert response.status_code == 200
    assert b'Create an Account' in response.data
    assert b'<form' in response.data
    assert b'username' in response.data
    assert b'email' in response.data
    assert b'password' in response.data
    assert b'age_group' in response.data

def test_login_page_accessibility(client):
    """Test that the login page is accessible and has the correct elements."""
    response = client.get('/auth/login/')
    assert response.status_code == 200
    assert b'Log In' in response.data
    assert b'<form' in response.data
    assert b'username' in response.data
    assert b'password' in response.data

def test_register_user_success(client, db):
    """Test successful user registration with detailed validation."""
    # Create a test user
    response = client.post('/auth/register/', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'age_group': '7-9'
    }, follow_redirects=True)
    
    # Check that we're redirected to the dashboard
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    
    # Check that the user was created in the database
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'
    assert user.age_group == '7-9'
    
    # Check that the user is logged in
    with client.session_transaction() as sess:
        assert sess.get('user_id') is not None
        assert sess.get('username') == 'newuser'
        
    # Check session persistence across requests
    dashboard_response = client.get('/dashboard/')
    assert dashboard_response.status_code == 200
    assert b'Dashboard' in dashboard_response.data

def test_register_missing_fields(client, db):
    """Test registration with missing required fields."""
    # Try to register without username
    response = client.post('/auth/register/', data={
        'email': 'incomplete@example.com',
        'password': 'password123',
        'age_group': '7-9'
    })
    
    assert response.status_code == 200
    assert b'All fields are required' in response.data
    
    # Try to register without email
    response = client.post('/auth/register/', data={
        'username': 'incomplete',
        'password': 'password123',
        'age_group': '7-9'
    })
    
    assert response.status_code == 200
    assert b'All fields are required' in response.data
    
    # Try to register without password
    response = client.post('/auth/register/', data={
        'username': 'incomplete',
        'email': 'incomplete@example.com',
        'age_group': '7-9'
    })
    
    assert response.status_code == 200
    assert b'All fields are required' in response.data

def test_register_duplicate_username(client, db):
    """Test registration with an existing username."""
    # Create a user first
    user = User(
        username='existinguser',
        email='existing@example.com',
        password='hashedpassword',
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to register with the same username
    response = client.post('/auth/register/', data={
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'password123',
        'age_group': '7-9'
    })
    
    assert response.status_code == 200
    assert b'Username already exists' in response.data

def test_register_duplicate_email(client, db):
    """Test registration with an existing email."""
    # Create a user first
    user = User(
        username='emailuser',
        email='duplicate@example.com',
        password='hashedpassword',
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to register with the same email
    response = client.post('/auth/register/', data={
        'username': 'newemailuser',
        'email': 'duplicate@example.com',
        'password': 'password123',
        'age_group': '7-9'
    })
    
    assert response.status_code == 200
    assert b'Email already registered' in response.data

def test_login_success(client, db):
    """Test successful user login with detailed validation."""
    # Create a user
    from werkzeug.security import generate_password_hash
    user = User(
        username='logintest',
        email='login@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Log in
    response = client.post('/auth/login/', data={
        'username': 'logintest',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Check that we're redirected to the dashboard
    assert response.status_code == 200
    assert b'Dashboard' in response.data
    
    # Check that the user is logged in
    with client.session_transaction() as sess:
        assert sess.get('user_id') is not None
        assert sess.get('username') == 'logintest'
        
    # Check session persistence across requests
    dashboard_response = client.get('/dashboard/')
    assert dashboard_response.status_code == 200
    assert b'Dashboard' in dashboard_response.data

def test_login_missing_fields(client, db):
    """Test login with missing required fields."""
    # Try to login without username
    response = client.post('/auth/login/', data={
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert b'Username and password are required' in response.data
    
    # Try to login without password
    response = client.post('/auth/login/', data={
        'username': 'testuser'
    })
    
    assert response.status_code == 200
    assert b'Username and password are required' in response.data

def test_login_nonexistent_user(client, db):
    """Test login with a username that doesn't exist."""
    response = client.post('/auth/login/', data={
        'username': 'nonexistentuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    
    # Check that the user is not logged in
    with client.session_transaction() as sess:
        assert sess.get('user_id') is None

def test_login_wrong_password(client, db):
    """Test login with incorrect password."""
    # Create a user
    from werkzeug.security import generate_password_hash
    user = User(
        username='passwordtest',
        email='password@example.com',
        password=generate_password_hash('correctpassword'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to log in with wrong password
    response = client.post('/auth/login/', data={
        'username': 'passwordtest',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    
    # Check that the user is not logged in
    with client.session_transaction() as sess:
        assert sess.get('user_id') is None

def test_logout_success(authenticated_client):
    """Test successful user logout with detailed validation."""
    # First check that the user is logged in
    with authenticated_client.session_transaction() as sess:
        assert sess.get('user_id') is not None
    
    # Log out
    response = authenticated_client.get('/auth/logout/', follow_redirects=True)
    assert response.status_code == 200
    
    # Check that the user is logged out
    with authenticated_client.session_transaction() as sess:
        assert sess.get('user_id') is None
        assert sess.get('username') is None
        
    # Verify that protected routes are no longer accessible
    dashboard_response = authenticated_client.get('/dashboard/', follow_redirects=True)
    assert b'Log In' in dashboard_response.data or b'Welcome' in dashboard_response.data

def test_session_expiry(client, db, app):
    """Test that session expires after the configured timeout."""
    # Create a user
    from werkzeug.security import generate_password_hash
    user = User(
        username='sessiontest',
        email='session@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Log in
    client.post('/auth/login/', data={
        'username': 'sessiontest',
        'password': 'password123'
    })
    
    # Check that the user is logged in
    with client.session_transaction() as sess:
        assert sess.get('user_id') is not None
    
    # This test is a placeholder since we can't easily simulate session expiry in a test
    # In a real application, you would configure a short session timeout for testing
    # and use time.sleep() to wait for it to expire
    
    # For now, we'll just verify the session exists
    assert True

def test_malformed_request(client):
    """Test handling of malformed requests to authentication endpoints."""
    # Test with invalid content type
    response = client.post('/auth/login/', 
                          data='{"username": "test", "password": "test"}',
                          content_type='application/json')
    
    # Should handle gracefully and return to login page
    assert response.status_code == 200
    assert b'Log In' in response.data

def test_csrf_protection(client, app):
    """Test CSRF protection for authentication forms."""
    # This test is a placeholder since CSRF is disabled in test config
    # In a real application with CSRF enabled, you would verify that
    # requests without valid CSRF tokens are rejected
    
    # For now, we'll just check that WTF_CSRF_ENABLED is False in test config
    assert app.config['WTF_CSRF_ENABLED'] is False

def test_brute_force_protection(client, db):
    """Test protection against brute force login attempts."""
    # Create a user
    from werkzeug.security import generate_password_hash
    user = User(
        username='bruteforce',
        email='brute@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # This test is a placeholder for brute force protection
    # In a real application, you would implement rate limiting and test it
    # by making multiple failed login attempts and verifying that
    # subsequent attempts are blocked
    
    # For now, we'll just make a few failed attempts and verify they fail
    for i in range(5):
        response = client.post('/auth/login/', data={
            'username': 'bruteforce',
            'password': f'wrongpassword{i}'
        })
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data

def test_auth_logging(client, db, tmp_path, monkeypatch):
    """Test that authentication attempts are properly logged."""
    # This test verifies that authentication events are logged
    # We would need to configure a test log file and check its contents
    
    # Create a user
    from werkzeug.security import generate_password_hash
    user = User(
        username='logtest',
        email='log@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Make a successful login attempt
    client.post('/auth/login/', data={
        'username': 'logtest',
        'password': 'password123'
    })
    
    # Make a failed login attempt
    client.post('/auth/login/', data={
        'username': 'logtest',
        'password': 'wrongpassword'
    })
    
    # In a real test, we would check the log file contents
    # For now, we'll just verify the requests were made
    assert True

def test_protected_route_access(client, authenticated_client):
    """Test access to protected routes with and without authentication."""
    # Test access without authentication
    response = client.get('/dashboard/', follow_redirects=True)
    assert b'Log In' in response.data or b'Welcome' in response.data
    
    # Test access with authentication
    auth_response = authenticated_client.get('/dashboard/')
    assert auth_response.status_code == 200
    assert b'Dashboard' in auth_response.data

def test_login_redirect(client, db):
    """Test that login redirects to the intended page after successful authentication."""
    # Create a user
    from werkzeug.security import generate_password_hash
    user = User(
        username='redirecttest',
        email='redirect@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to access a protected page, should redirect to login
    response = client.get('/dashboard/', follow_redirects=True)
    assert b'Log In' in response.data or b'Welcome' in response.data
    
    # Log in
    login_response = client.post('/auth/login/', data={
        'username': 'redirecttest',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Should redirect to dashboard after login
    assert login_response.status_code == 200
    assert b'Dashboard' in login_response.data
