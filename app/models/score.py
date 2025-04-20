from app import db
from datetime import datetime

class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Overall score
    total_score = db.Column(db.Float, nullable=False)
    max_possible_score = db.Column(db.Float, nullable=False)
    
    # Detailed scoring
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    partial_credits = db.Column(db.Float, default=0.0)
    
    # Time tracking
    time_taken = db.Column(db.Integer)  # Time taken in seconds
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Additional metadata
    answers_data = db.Column(db.JSON)  # Store detailed answer data for each question
    
    def __repr__(self):
        return f'<Score {self.id}>' 