from flask import Blueprint, render_template, session, redirect, url_for, flash

dashboard_bp = Blueprint('dashboard_bp', __name__)

@dashboard_bp.route('/')
def index():
    """Display the user dashboard."""
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to access your dashboard!', 'error')
        return redirect(url_for('auth_bp.login'))
    
    # Get username from session
    username = session.get('username', 'User')
    
    print(f"Rendering dashboard for user: {username}")
    return render_template('dashboard/index.html', username=username)

@dashboard_bp.route('/progress')
def progress():
    """Display user progress."""
    if 'user_id' not in session:
        flash('Please log in to view your progress!', 'error')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('dashboard/progress.html')

@dashboard_bp.route('/achievements')
def achievements():
    """Display user achievements."""
    if 'user_id' not in session:
        flash('Please log in to view your achievements!', 'error')
        return redirect(url_for('auth_bp.login'))
    
    return render_template('dashboard/achievements.html')
