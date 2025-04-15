from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app import db
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/subjects')
@login_required
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{
        'id': subject.id,
        'name': subject.name,
        'description': subject.description,
        'chapters_count': len(subject.chapters)
    } for subject in subjects])

@bp.route('/subjects/<int:subject_id>/chapters')
@login_required
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description,
        'quizzes_count': len(chapter.quizzes)
    } for chapter in chapters])

@bp.route('/chapters/<int:chapter_id>/quizzes')
@login_required
def get_quizzes(chapter_id):
    quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
    return jsonify([{
        'id': quiz.id,
        'date_of_quiz': quiz.date_of_quiz.strftime('%Y-%m-%d %H:%M'),
        'time_duration': quiz.time_duration,
        'questions_count': len(quiz.questions),
        'attempts_count': len(quiz.scores)
    } for quiz in quizzes])

@bp.route('/quizzes/<int:quiz_id>/stats')
@login_required
def get_quiz_stats(quiz_id):
    scores = Score.query.filter_by(quiz_id=quiz_id).all()
    if not scores:
        return jsonify({
            'total_attempts': 0,
            'average_score': 0,
            'highest_score': 0,
            'pass_rate': 0
        })
    
    total_attempts = len(scores)
    average_score = sum(score.total_scored for score in scores) / total_attempts
    highest_score = max(score.total_scored for score in scores)
    passing_scores = sum(1 for score in scores if (score.total_scored / score.total_questions) >= 0.6)
    
    return jsonify({
        'total_attempts': total_attempts,
        'average_score': round(average_score, 2),
        'highest_score': highest_score,
        'pass_rate': round((passing_scores / total_attempts) * 100, 2)
    })

@bp.route('/user/performance')
@login_required
def get_user_performance():
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).all()
    total_quizzes = len(scores)
    if not scores:
        return jsonify({
            'total_quizzes': 0,
            'average_score': 0,
            'highest_score': 0,
            'recent_scores': []
        })
    
    average_score = sum((score.total_scored / score.total_questions) * 100 for score in scores) / total_quizzes
    highest_score = max((score.total_scored / score.total_questions) * 100 for score in scores)
    
    recent_scores = [{
        'quiz_name': f"{score.quiz.chapter.subject.name} - {score.quiz.chapter.name}",
        'score': score.total_scored,
        'total': score.total_questions,
        'percentage': round((score.total_scored / score.total_questions) * 100, 2),
        'date': score.timestamp.strftime('%Y-%m-%d %H:%M')
    } for score in scores[:5]]
    
    return jsonify({
        'total_quizzes': total_quizzes,
        'average_score': round(average_score, 2),
        'highest_score': round(highest_score, 2),
        'recent_scores': recent_scores
    }) 