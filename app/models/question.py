from app import db
from datetime import datetime

class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quiz.id'), nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # 'mcq', 'true_false', 'fill_blank', 'matching', 'short_answer', 'image'
    question_statement = db.Column(db.Text, nullable=False)
    marks = db.Column(db.Float, nullable=True, default=1.0)  # Make marks nullable initially
    
    # For MCQ and True/False
    option1 = db.Column(db.String(200))
    option2 = db.Column(db.String(200))
    option3 = db.Column(db.String(200))
    option4 = db.Column(db.String(200))
    correct_option = db.Column(db.Integer)  # 1, 2, 3, or 4 for MCQ, 1 or 2 for True/False
    
    # For Fill in the Blank
    correct_answer = db.Column(db.String(200))
    
    # For Matching Pairs
    matching_pairs = db.Column(db.JSON)  # Store as JSON: {"pair1": ["left", "right"], "pair2": ["left", "right"]}
    
    # For Short Answer
    expected_answer = db.Column(db.Text)
    
    # For Image-based questions
    image_url = db.Column(db.String(500))
    
    # Difficulty and Tags
    difficulty = db.Column(db.Integer, default=1)  # 1-5 scale
    tags = db.Column(db.String(500))  # Comma-separated tags
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Question {self.id}>' 