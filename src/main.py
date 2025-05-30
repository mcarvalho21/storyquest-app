import os
import sys
from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Initialize Flask app
app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
app.config['SECRET_KEY'] = 'storyquest_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storyquest.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Import models and initialize database
from src.models.user import db
db.init_app(app)

# Import all models after db initialization
from src.models.user import User
from src.models.story import Story
from src.models.character import Character
from src.models.setting import Setting
from src.models.story_element import StoryElement
from src.models.achievement import Achievement

# Import routes after app and model initialization
from src.routes.auth import auth_bp
from src.routes.dashboard import dashboard_bp
from src.routes.story import story_bp
from src.routes.asset import asset_bp
from src.routes.progress import progress_bp
from src.routes.viral import viral_bp
from src.routes.main import main_bp

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
app.register_blueprint(story_bp, url_prefix='/story')
app.register_blueprint(asset_bp, url_prefix='/asset')
app.register_blueprint(progress_bp, url_prefix='/progress')
app.register_blueprint(viral_bp, url_prefix='/viral')
app.register_blueprint(main_bp)

# Create database tables
with app.app_context():
    # Drop all tables and recreate them (early development best practice)
    db.drop_all()
    db.create_all()
    print("Database tables dropped and recreated successfully")

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    print(f"404 error: {e}")
    print(f"Template folder: {app.template_folder}")
    print(f"Template exists: {os.path.exists(os.path.join(app.template_folder, '404.html'))}")
    try:
        # Updated to use the template in the root templates directory
        return render_template('404.html'), 404
    except Exception as ex:
        print(f"Error rendering 404 template: {ex}")
        return "Page not found", 404

@app.errorhandler(500)
def internal_server_error(e):
    print(f"500 error: {e}")
    try:
        # Updated to use the template in the root templates directory
        return render_template('500.html'), 500
    except Exception as ex:
        print(f"Error rendering 500 template: {ex}")
        return "Internal server error", 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
