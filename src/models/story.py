from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Story(db.Model):
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    age_group = db.Column(db.String(10), nullable=False)
    theme = db.Column(db.String(50), nullable=True)
    is_shared = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=False)
    is_complete = db.Column(db.Boolean, default=False)
    is_draft = db.Column(db.Boolean, default=False)
    content = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    share_url = db.Column(db.String(255), nullable=True)
    share_message = db.Column(db.Text, nullable=True)
    share_date = db.Column(db.DateTime, nullable=True)
    like_count = db.Column(db.Integer, default=0)
    view_count = db.Column(db.Integer, default=0)
    submission_date = db.Column(db.DateTime, nullable=True)
    is_challenge_winner = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=True)
    
    # Use string-based relationships to avoid circular imports
    characters = db.relationship('Character', backref='story', lazy=True, cascade="all, delete-orphan")
    settings = db.relationship('Setting', backref='story', lazy=True, cascade="all, delete-orphan")
    story_elements = db.relationship('StoryElement', backref='story', lazy=True, cascade="all, delete-orphan")
    progress = db.relationship('Progress', backref='story', lazy=True, cascade="all, delete-orphan")
    
    # Note: User relationship is defined in the User model with backref='author'
    
    @property
    def author(self):
        """Return the author of the story (for template compatibility)"""
        from src.models.user import User
        return User.get_by_id(self.user_id)
    
    @classmethod
    def get_by_id(cls, story_id):
        """Get story by ID using SQLAlchemy 2.0 compatible method"""
        return db.session.get(cls, story_id)
    
    @classmethod
    def get_user_stories(cls, user_id, include_drafts=False):
        """Get all stories by a specific user"""
        query = cls.query.filter_by(user_id=user_id)
        if not include_drafts:
            query = query.filter_by(is_draft=False)
        return query.order_by(cls.updated_at.desc()).all()
    
    @classmethod
    def get_public_stories(cls, limit=10):
        """Get public stories with efficient query"""
        return cls.query.filter_by(is_public=True).order_by(cls.share_date.desc()).limit(limit).all()
    
    @classmethod
    def get_featured_stories(cls, limit=6):
        """Get featured stories (most viewed/liked public stories)"""
        return cls.query.filter_by(is_public=True).order_by(
            cls.view_count.desc(), cls.like_count.desc(), cls.created_at.desc()
        ).limit(limit).all()
    
    def __repr__(self):
        return f'<Story {self.title}>'
