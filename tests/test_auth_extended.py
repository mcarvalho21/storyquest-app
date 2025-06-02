import pytest
from flask import url_for, session
from unittest.mock import patch, MagicMock
from werkzeug.security import generate_password_hash
from src.models.user import User
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

def test_register_with_missing_fields(client):
    """Test registration with missing required fields."""
    # Test missing username
    response = client.post('/auth/register', data={
        'email': 'missing@example.com',
        'password': 'password123',
        'age_group': '7-9'
    })
    assert response.status_code == 200
    assert b'All fields are required' in response.data
    
    # Test missing email
    response = client.post('/auth/register', data={
        'username': 'missingfields',
        'password': 'password123',
        'age_group': '7-9'
    })
    assert response.status_code == 200
    assert b'All fields are required' in response.data
    
    # Test missing password
    response = client.post('/auth/register', data={
        'username': 'missingfields',
        'email': 'missing@example.com',
        'age_group': '7-9'
    })
    assert response.status_code == 200
    assert b'All fields are required' in response.data

def test_register_with_existing_username(client, db):
    """Test registration with an existing username."""
    # Create a user first
    user = User(
        username='existinguser',
        email='existing@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to register with the same username
    response = client.post('/auth/register', data={
        'username': 'existinguser',
        'email': 'new@example.com',
        'password': 'password123',
        'age_group': '7-9'
    })
    assert response.status_code == 200
    assert b'Username already exists' in response.data

def test_register_with_existing_email(client, db):
    """Test registration with an existing email."""
    # Create a user first
    user = User(
        username='emailuser',
        email='duplicate@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to register with the same email
    response = client.post('/auth/register', data={
        'username': 'newemailuser',
        'email': 'duplicate@example.com',
        'password': 'password123',
        'age_group': '7-9'
    })
    assert response.status_code == 200
    assert b'Email already registered' in response.data

def test_login_with_missing_fields(client):
    """Test login with missing required fields."""
    # Test missing username
    response = client.post('/auth/login', data={
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b'Username and password are required' in response.data
    
    # Test missing password
    response = client.post('/auth/login', data={
        'username': 'testuser'
    })
    assert response.status_code == 200
    assert b'Username and password are required' in response.data

def test_login_with_nonexistent_user(client):
    """Test login with a username that doesn't exist."""
    response = client.post('/auth/login', data={
        'username': 'nonexistentuser',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data

@patch('src.routes.auth.db.session.commit')
def test_register_database_error(mock_commit, client, db):
    """Test registration with a database error."""
    # Mock a database error during commit
    mock_commit.side_effect = SQLAlchemyError("Database error")
    
    # Attempt to register
    response = client.post('/auth/register', data={
        'username': 'dberroruser',
        'email': 'dberror@example.com',
        'password': 'password123',
        'age_group': '7-9'
    })
    
    # Verify error handling
    assert response.status_code == 200
    assert b'An error occurred during registration' in response.data
    
    # Verify user was not created
    user = User.query.filter_by(username='dberroruser').first()
    assert user is None

@patch('src.routes.auth.User.query')
def test_login_database_error(mock_query, client):
    """Test login with a database error."""
    # Mock a database error during query
    mock_query.filter_by.side_effect = SQLAlchemyError("Database error")
    
    # Attempt to login
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    
    # Verify error handling
    assert response.status_code == 200
    assert b'An error occurred during login' in response.data

def test_session_persistence(client, db):
    """Test that session persists correctly after login."""
    # Create a user
    user = User(
        username='sessiontest',
        email='session@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Log in
    client.post('/auth/login', data={
        'username': 'sessiontest',
        'password': 'password123'
    })
    
    # Check session after login
    with client.session_transaction() as sess:
        user_id = sess.get('user_id')
        username = sess.get('username')
    
    assert user_id is not None
    assert username == 'sessiontest'
    
    # Make another request and verify session is maintained
    response = client.get('/')
    
    # Check session again
    with client.session_transaction() as sess:
        assert sess.get('user_id') == user_id
        assert sess.get('username') == username

@patch('src.routes.auth.session')
def test_session_corruption(mock_session, client, db):
    """Test handling of session corruption during login."""
    # Create a user
    user = User(
        username='corrupttest',
        email='corrupt@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Mock session to raise an exception when setting items
    mock_session.__setitem__.side_effect = Exception("Session corruption")
    
    # Attempt to login
    response = client.post('/auth/login', data={
        'username': 'corrupttest',
        'password': 'password123'
    })
    
    # Verify error handling
    assert response.status_code == 200
    assert b'An error occurred during login' in response.data

def test_concurrent_login_attempts(client, db):
    """Test handling of concurrent login attempts for the same user."""
    # Create a user
    user = User(
        username='concurrentuser',
        email='concurrent@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # First login attempt
    response1 = client.post('/auth/login', data={
        'username': 'concurrentuser',
        'password': 'password123'
    })
    assert response1.status_code == 302  # Successful redirect
    
    # Second login attempt (should also succeed as we're not preventing concurrent logins)
    response2 = client.post('/auth/login', data={
        'username': 'concurrentuser',
        'password': 'password123'
    })
    assert response2.status_code == 302  # Successful redirect

def test_logout_without_login(client):
    """Test logout behavior when not logged in."""
    # Attempt to logout without being logged in
    response = client.get('/auth/logout')
    
    # Should redirect to main page
    assert response.status_code == 302
    
    # Session should still be empty
    with client.session_transaction() as sess:
        assert sess.get('user_id') is None
        assert sess.get('username') is None

@patch('src.routes.auth.session')
def test_logout_session_error(mock_session, authenticated_client):
    """Test logout with session error."""
    # Mock session.pop to raise an exception
    mock_session.pop.side_effect = Exception("Session error during logout")
    
    # Attempt to logout
    response = authenticated_client.get('/auth/logout')
    
    # Should still redirect to main page despite error
    assert response.status_code == 302
