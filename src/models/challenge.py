from src.models.user import db

class Challenge(db.Model):
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    age_group = db.Column(db.String(10), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    stories = db.relationship('Story', backref='challenge', lazy=True)
    
    def __repr__(self):
        return f'<Challenge {self.title}>'
