from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Progress(db.Model):
    __tablename__ = 'progress'
    
    id = db.Column(db.Integer, primary_key=True)
    current_step = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    def __repr__(self):
        return f'<Progress for Story {self.story_id} at step {self.current_step}>'
