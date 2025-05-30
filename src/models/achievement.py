from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon_path = db.Column(db.String(255), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    achieved_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Achievement {self.name}>'
