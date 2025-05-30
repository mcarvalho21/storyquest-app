from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StoryElement(db.Model):
    __tablename__ = 'story_elements'
    
    id = db.Column(db.Integer, primary_key=True)
    element_type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f'<StoryElement {self.element_type} at position {self.position}>'
