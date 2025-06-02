import pytest
from flask import url_for, session
from src.models.user import User

def test_register_page(client):
    """Test that the register page loads correctly."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Create an Account' in response.data

def test_login_page(client):
    """Test that the login page loads correctly."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Log In' in response.data

def test_register_user(client, db):
    """Test user registration."""
    # Create a test user
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'password123',
        'age_group': '7-9'
    }, follow_redirects=False)  # Don't follow redirects to avoid BuildError
    
    # Check redirect status code
    assert response.status_code == 302
    
    # Check that the user was created in the database
    user = User.query.filter_by(username='newuser').first()
    assert user is not None
    assert user.email == 'newuser@example.com'
    assert user.age_group == '7-9'
    
    # Check that the user is logged in
    with client.session_transaction() as sess:
        assert sess.get('user_id') is not None
        assert sess.get('username') == 'newuser'

def test_login_user(client, db):
    """Test user login."""
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
    response = client.post('/auth/login', data={
        'username': 'logintest',
        'password': 'password123'
    }, follow_redirects=False)  # Don't follow redirects to avoid BuildError
    
    # Check redirect status code
    assert response.status_code == 302
    
    # Check that the user is logged in
    with client.session_transaction() as sess:
        assert sess.get('user_id') is not None
        assert sess.get('username') == 'logintest'

def test_logout(authenticated_client):
    """Test user logout."""
    # First check that the user is logged in
    with authenticated_client.session_transaction() as sess:
        assert sess.get('user_id') is not None
    
    # Log out
    response = authenticated_client.get('/auth/logout', follow_redirects=False)  # Don't follow redirects
    assert response.status_code == 302
    
    # Check that the user is logged out
    with authenticated_client.session_transaction() as sess:
        assert sess.get('user_id') is None
        assert sess.get('username') is None

def test_invalid_login(client, db):
    """Test login with invalid credentials."""
    # Create a user
    from werkzeug.security import generate_password_hash
    user = User(
        username='invalidtest',
        email='invalid@example.com',
        password=generate_password_hash('password123'),
        age_group='7-9'
    )
    db.session.add(user)
    db.session.commit()
    
    # Try to log in with wrong password
    response = client.post('/auth/login', data={
        'username': 'invalidtest',
        'password': 'wrongpassword'
    })
    
    assert response.status_code == 200
    assert b'Invalid username or password' in response.data
    
    # Check that the user is not logged in
    with client.session_transaction() as sess:
        assert sess.get('user_id') is None
