from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age_group = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # Define relationships using string references to avoid circular imports
    # Remove direct reference to Story.user_id which is causing the error
    stories = db.relationship('Story', backref='author', lazy=True)
    achievements = db.relationship('Achievement', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
