from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Use string-based relationships to avoid circular imports
    stories = db.relationship('Story', backref='author', lazy=True)
    achievements = db.relationship('Achievement', secondary='user_achievements', lazy='subquery',
                                  backref=db.backref('users', lazy=True))
    
    def set_password(self, password):
        """Set password hash for user"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches stored hash"""
        return check_password_hash(self.password, password)
    
    @classmethod
    def get_by_id(cls, user_id):
        """Get user by ID using SQLAlchemy 2.0 compatible method"""
        return db.session.get(cls, user_id)
    
    @classmethod
    def get_by_username(cls, username):
        """Get user by username"""
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        return cls.query.filter_by(email=email).first()
    
    def __repr__(self):
        return f'<User {self.username}>'

# Association table for many-to-many relationship between users and achievements
user_achievements = db.Table('user_achievements',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('achievement_id', db.Integer, db.ForeignKey('achievements.id'), primary_key=True)
)
