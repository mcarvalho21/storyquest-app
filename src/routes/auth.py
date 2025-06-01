from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db, User
from src.utils.logging_config import auth_logger, log_authentication_attempt, log_session_state
import traceback

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
@auth_bp.route('/register/', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age_group = request.form.get('age_group', '7-9')
        
        auth_logger.debug(f"Registration attempt - Username: {username}, Email: {email}, Age group: {age_group}")
        
        # Validate form data
        if not username or not email or not password:
            error_msg = f"Registration validation failed - Missing fields: " + \
                        f"{'username ' if not username else ''}" + \
                        f"{'email ' if not email else ''}" + \
                        f"{'password' if not password else ''}"
            auth_logger.warning(error_msg)
            flash('All fields are required!', 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            auth_logger.warning(f"Registration failed - Username already exists: {username}")
            flash('Username already exists!', 'error')
            return render_template('auth/register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            auth_logger.warning(f"Registration failed - Email already registered: {email}")
            flash('Email already registered!', 'error')
            return render_template('auth/register.html')
        
        # Create new user
        try:
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                age_group=age_group
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Log the user in
            session['user_id'] = new_user.id
            session['username'] = new_user.username
            
            log_authentication_attempt(True, username)
            log_session_state()
            
            auth_logger.info(f"User registered successfully: {username} (ID: {new_user.id})")
            return redirect(url_for('dashboard_bp.index'))
        except Exception as e:
            db.session.rollback()
            error_details = traceback.format_exc()
            auth_logger.error(f"Error registering user: {username}", exc_info=True)
            auth_logger.debug(f"Registration error details: {error_details}")
            
            log_authentication_attempt(False, username, e)
            
            flash('An error occurred during registration!', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/login/', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        auth_logger.debug(f"Login attempt - Username: {username}")
        
        # Validate form data
        if not username or not password:
            auth_logger.warning(f"Login validation failed - Missing fields: " + 
                              f"{'username ' if not username else ''}" + 
                              f"{'password' if not password else ''}")
            flash('Username and password are required!', 'error')
            return render_template('auth/login.html')
        
        # Check if user exists
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                auth_logger.warning(f"Login failed - User not found: {username}")
                log_authentication_attempt(False, username)
                flash('Invalid username or password!', 'error')
                return render_template('auth/login.html')
            
            if not check_password_hash(user.password, password):
                auth_logger.warning(f"Login failed - Invalid password for user: {username}")
                log_authentication_attempt(False, username)
                flash('Invalid username or password!', 'error')
                return render_template('auth/login.html')
            
            # Log the user in
            session['user_id'] = user.id
            session['username'] = user.username
            
            auth_logger.info(f"User logged in successfully: {username} (ID: {user.id})")
            log_authentication_attempt(True, username)
            log_session_state()
            
            # Debug check for session after login
            auth_logger.debug(f"Session after login: user_id={session.get('user_id')}, username={session.get('username')}")
            
            return redirect(url_for('dashboard_bp.index'))
        except Exception as e:
            error_details = traceback.format_exc()
            auth_logger.error(f"Error during login for user: {username}", exc_info=True)
            auth_logger.debug(f"Login error details: {error_details}")
            
            log_authentication_attempt(False, username, e)
            
            flash('An error occurred during login!', 'error')
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@auth_bp.route('/logout/')
def logout():
    """Log out the current user."""
    username = session.get('username', 'Unknown')
    user_id = session.get('user_id', 'Unknown')
    
    auth_logger.debug(f"Logout attempt - Username: {username}, User ID: {user_id}")
    log_session_state()
    
    try:
        session.pop('user_id', None)
        session.pop('username', None)
        
        auth_logger.info(f"User logged out successfully: {username} (ID: {user_id})")
        
        # Debug check for session after logout
        auth_logger.debug("Session after logout: " + str({k: v for k, v in session.items()} if session else {}))
        
        return redirect(url_for('main.index'))
    except Exception as e:
        error_details = traceback.format_exc()
        auth_logger.error(f"Error during logout for user: {username}", exc_info=True)
        auth_logger.debug(f"Logout error details: {error_details}")
        
        # Try to redirect anyway
        return redirect(url_for('main.index'))
