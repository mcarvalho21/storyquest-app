from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Story(db.Model):
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    is_complete = db.Column(db.Boolean, default=False)
    age_group = db.Column(db.String(20), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # Define relationships using string references
    characters = db.relationship('Character', backref='story', lazy=True, cascade='all, delete-orphan')
    settings = db.relationship('Setting', backref='story', lazy=True, cascade='all, delete-orphan')
    story_elements = db.relationship('StoryElement', backref='story', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Story {self.title}>'
