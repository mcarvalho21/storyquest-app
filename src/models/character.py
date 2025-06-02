from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Character(db.Model):
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    traits = db.Column(db.String(200), nullable=True)
    age = db.Column(db.String(50), nullable=True)  # Added age field to match test expectations
    personality = db.Column(db.String(200), nullable=True)  # Added personality field to match test expectations
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Foreign keys
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Character {self.name}>'
