from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app.models.user import User
from app import db
from datetime import datetime
from sqlalchemy import func

bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@bp.route('/<int:quiz_id>/details')
@login_required
def quiz_details(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    user_score = Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first()
    return render_template('quiz/details.html', quiz=quiz, questions=questions, user_score=user_score)

@bp.route('/<int:quiz_id>/leaderboard')
@login_required
def leaderboard(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    scores = Score.query.filter_by(quiz_id=quiz_id).order_by(Score.total_scored.desc()).all()
    
    # Calculate statistics
    total_attempts = len(scores)
    if total_attempts > 0:
        avg_score = sum((score.total_scored / score.total_questions) * 100 for score in scores) / total_attempts
        pass_count = sum(1 for score in scores if (score.total_scored / score.total_questions) * 100 >= 60)
        pass_rate = (pass_count / total_attempts) * 100
    else:
        avg_score = 0
        pass_count = 0
        pass_rate = 0
    fail_count = total_attempts - pass_count
    
    # Get user's best score
    user_scores = [score for score in scores if score.user_id == current_user.id]
    user_best_score = max((score.total_scored / score.total_questions) * 100 for score in user_scores) if user_scores else 0
    
    # Prepare leaderboard data
    leaderboard = []
    for score in scores:
        user = User.query.get(score.user_id)
        percentage = (score.total_scored / score.total_questions) * 100
        leaderboard.append({
            'user_id': user.id,
            'user_name': user.full_name,
            'percentage': percentage,
            'time_taken': score.time_taken,
            'timestamp': score.timestamp
        })
    
    return render_template('quiz/leaderboard.html',
                         quiz=quiz,
                         leaderboard=leaderboard,
                         avg_score=avg_score,
                         pass_rate=pass_rate,
                         pass_count=pass_count,
                         fail_count=fail_count,
                         user_best_score=user_best_score)

@bp.route('/api/<int:quiz_id>/stats')
@login_required
def quiz_stats(quiz_id):
    scores = Score.query.filter_by(quiz_id=quiz_id).all()
    total_attempts = len(scores)
    if total_attempts == 0:
        return jsonify({
            'total_attempts': 0,
            'average_score': 0,
            'highest_score': 0,
            'lowest_score': 0
        })
    
    average_score = sum(score.total_scored for score in scores) / total_attempts
    highest_score = max(score.total_scored for score in scores)
    lowest_score = min(score.total_scored for score in scores)
    
    return jsonify({
        'total_attempts': total_attempts,
        'average_score': round(average_score, 2),
        'highest_score': highest_score,
        'lowest_score': lowest_score
    }) 