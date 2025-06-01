import os
import sys
from flask import Flask, render_template, session, redirect, url_for, flash, request, g
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import logging configuration first
from src.utils.logging_config import logger

# Import database and models
from src.models import db, User, Story, Character, Setting, StoryElement, Achievement, Progress, Challenge

# Import routes
from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp
from src.routes.story import story_bp
from src.routes.progress import progress_bp
from src.routes.viral import viral_bp
from src.routes.main import main_bp
from src.routes.asset import asset_bp

def create_app():
    app = Flask(__name__)
    
    # Configure the app
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_for_development')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storyquest.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Register blueprints with consistent naming and strict_slashes=False to prevent 308 redirects
    app.register_blueprint(auth_bp, url_prefix='/auth', strict_slashes=False)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard', strict_slashes=False)
    app.register_blueprint(story_bp, url_prefix='/story', strict_slashes=False)
    app.register_blueprint(progress_bp, url_prefix='/progress', strict_slashes=False)
    app.register_blueprint(viral_bp, url_prefix='/viral', strict_slashes=False)
    app.register_blueprint(asset_bp, url_prefix='/asset', strict_slashes=False)
    app.register_blueprint(main_bp, strict_slashes=False)
    
    # Add authentication context processor to make session data available to all templates
    @app.context_processor
    def inject_auth_status():
        return {
            'is_authenticated': session.get('user_id') is not None,
            'username': session.get('username')
        }
    
    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        logger.warning(f"404 error: {request.path} - {e}")
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        logger.error(f"500 error: {request.path} - {e}", exc_info=True)
        return render_template('errors/500.html'), 500
    
    # Log all requests for debugging
    @app.before_request
    def log_request():
        logger.debug(f"Request: {request.method} {request.path} - Session: {session.get('user_id')}")
    
    # Log all responses for debugging
    @app.after_request
    def log_response(response):
        logger.debug(f"Response: {response.status_code} - Session: {session.get('user_id')}")
        return response
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create admin user if it doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@storyquest.com',
                password=generate_password_hash('admin123'),
                age_group='adult'
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Admin user created")
    
    logger.info("Application initialized successfully")
    return app

app = create_app()

if __name__ == '__main__':
    logger.info("Starting StoryQuest application")
    app.run(host='0.0.0.0', port=5000, debug=True)
