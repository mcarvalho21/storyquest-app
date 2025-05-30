from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db, User

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user account."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        age_group = request.form.get('age_group', '7-9')
        
        # Validate form data
        if not username or not email or not password:
            flash('All fields are required!', 'error')
            return render_template('auth/register.html')
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'error')
            return render_template('auth/register.html')
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
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
            
            print(f"User registered successfully: {username}")
            return redirect(url_for('dashboard_bp.index'))
        except Exception as e:
            print(f"Error registering user: {e}")
            db.session.rollback()
            flash('An error occurred during registration!', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in an existing user."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Validate form data
        if not username or not password:
            flash('Username and password are required!', 'error')
            return render_template('auth/login.html')
        
        # Check if user exists
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid username or password!', 'error')
            return render_template('auth/login.html')
        
        # Log the user in
        session['user_id'] = user.id
        session['username'] = user.username
        
        return redirect(url_for('dashboard_bp.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """Log out the current user."""
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('main_bp.index'))
