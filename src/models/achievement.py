from flask_sqlalchemy import SQLAlchemy
from src.models.user import db

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    criteria = db.Column(db.Text, nullable=True)
    badge_image = db.Column(db.String(200), nullable=True)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    @classmethod
    def get_by_id(cls, achievement_id):
        """Get achievement by ID using SQLAlchemy 2.0 compatible method"""
        return db.session.get(cls, achievement_id)
    
    @classmethod
    def get_by_name(cls, name):
        """Get achievement by name"""
        return cls.query.filter_by(name=name).first()
    
    @classmethod
    def get_all_achievements(cls):
        """Get all achievements with efficient query"""
        return cls.query.order_by(cls.points.desc()).all()
    
    @classmethod
    def get_user_achievements(cls, user):
        """Get achievements earned by a specific user"""
        return user.achievements
    
    @classmethod
    def get_available_achievements(cls, user):
        """Get achievements not yet earned by a specific user"""
        earned_ids = [a.id for a in user.achievements]
        if earned_ids:
            return cls.query.filter(~cls.id.in_(earned_ids)).all()
        else:
            return cls.get_all_achievements()
    
    def __repr__(self):
        return f'<Achievement {self.name}>'
