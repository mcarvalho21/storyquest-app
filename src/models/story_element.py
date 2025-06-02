from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class StoryElement(db.Model):
    __tablename__ = 'story_elements'
    
    id = db.Column(db.Integer, primary_key=True)
    element_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Foreign keys
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    
    def __repr__(self):
        return f'<StoryElement {self.element_type} at position {self.position}>'
