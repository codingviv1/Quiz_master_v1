from app import db
from datetime import datetime

class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    remarks = db.Column(db.Text)
    
    # Custom marking system
    correct_answer_points = db.Column(db.Float, default=1.0)  # Points for correct answer
    wrong_answer_penalty = db.Column(db.Float, default=0.0)   # Negative points for wrong answer
    partial_credit = db.Column(db.Boolean, default=False)      # Whether to allow partial credit
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    scores = db.relationship('Score', backref='quiz', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Quiz {self.id}>' 