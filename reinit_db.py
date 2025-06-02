import os
import sys
from flask import Flask

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import database and models
from src.models import db

def reinit_db():
    """Drop and recreate all database tables."""
    app = Flask(__name__)
    
    # Configure the app with correct database path
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'storyquest.db')
    db_dir = os.path.dirname(db_path)
    
    # Ensure the directory exists
    if not os.path.exists(db_dir):
        print(f"Creating database directory: {db_dir}")
        os.makedirs(db_dir, exist_ok=True)
    
    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database reinitialized successfully!")

if __name__ == '__main__':
    reinit_db()
