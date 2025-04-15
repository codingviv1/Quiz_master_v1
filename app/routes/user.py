from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.score import Score
from app import db
from datetime import datetime

bp = Blueprint('user', __name__)

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    
    subjects = Subject.query.all()
    recent_scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).limit(5).all()
    return render_template('user/dashboard.html', subjects=subjects, recent_scores=recent_scores)

@bp.route('/subjects')
@login_required
def list_subjects():
    subjects = Subject.query.all()
    # Get list of completed quizzes for this user
    completed_quizzes = [score.quiz_id for score in Score.query.filter_by(user_id=current_user.id).all()]
    return render_template('user/subjects.html', subjects=subjects, completed_quizzes=completed_quizzes)

@bp.route('/subjects/<int:subject_id>/chapters')
@login_required
def list_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    chapters = subject.chapters
    # Get list of completed quizzes for this user
    completed_quizzes = [score.quiz_id for score in Score.query.filter_by(user_id=current_user.id).all()]
    return render_template('user/chapters.html', subject=subject, chapters=chapters, completed_quizzes=completed_quizzes)

@bp.route('/chapters/<int:chapter_id>/quizzes')
@login_required
def list_quizzes(chapter_id):
    try:
        # Get the chapter and its quizzes
        chapter = Chapter.query.get_or_404(chapter_id)
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        
        # Get list of completed quizzes for this user
        completed_quizzes = [score.quiz_id for score in Score.query.filter_by(user_id=current_user.id).all()]
        
        # Get current time for quiz availability check
        current_time = datetime.utcnow()
        
        # Convert quiz dates to UTC for proper comparison
        for quiz in quizzes:
            if isinstance(quiz.date, datetime):
                quiz.date = quiz.date.replace(tzinfo=None)
        
        return render_template(
            'user/quizzes.html',
            chapter=chapter,
            quizzes=quizzes,
            completed_quizzes=completed_quizzes,
            now=current_time
        )
        
    except Exception as e:
        import traceback
        print(f"Error in list_quizzes: {str(e)}")
        print(traceback.format_exc())
        flash('Unable to load quizzes. Please try again later.', 'error')
        return redirect(url_for('user.list_subjects'))

@bp.route('/quiz/<int:quiz_id>')
@login_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    # Check if user has already taken this quiz
    existing_score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first()
    if existing_score:
        flash('You have already taken this quiz!', 'warning')
        return redirect(url_for('user.quiz_result', quiz_id=quiz_id))
    
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template('user/take_quiz.html', quiz=quiz, questions=questions)

@bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def submit_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        
        if not questions:
            flash('No questions found for this quiz!', 'error')
            return redirect(url_for('user.list_quizzes', chapter_id=quiz.chapter_id))
        
        total_questions = len(questions)
        correct_answers = 0
        
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if not user_answer:
                flash('Please answer all questions!', 'error')
                return redirect(url_for('user.start_quiz', quiz_id=quiz_id))
            
            if int(user_answer) == question.correct_option:
                correct_answers += 1
        
        score = Score(
            quiz_id=quiz_id,
            user_id=current_user.id,
            total_scored=correct_answers,
            total_questions=total_questions,
            time_taken=request.form.get('time_taken', '00:00')
        )
        db.session.add(score)
        db.session.commit()
        
        percentage = (correct_answers / total_questions) * 100
        flash(f'Quiz submitted successfully! You scored {percentage:.1f}%', 'success')
        return redirect(url_for('user.dashboard'))
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred while submitting the quiz: {str(e)}', 'error')
        return redirect(url_for('user.start_quiz', quiz_id=quiz_id))

@bp.route('/quiz/<int:quiz_id>/result')
@login_required
def quiz_result(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first_or_404()
    return render_template('user/quiz_result.html', quiz=quiz, score=score)

@bp.route('/scores')
@login_required
def view_scores():
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).all()
    return render_template('user/scores.html', scores=scores)

@bp.route('/api/user/scores')
@login_required
def get_user_scores():
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.timestamp.desc()).all()
    return jsonify([{
        'quiz_name': score.quiz.chapter.name,
        'score': score.total_scored,
        'total': score.total_questions,
        'percentage': (score.total_scored / score.total_questions) * 100,
        'date': score.timestamp.strftime('%Y-%m-%d %H:%M')
    } for score in scores])

@bp.route('/debug/chapter/<int:chapter_id>')
@login_required
def debug_chapter(chapter_id):
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        
        debug_info = {
            'chapter_id': chapter.id,
            'chapter_name': chapter.name,
            'subject_id': chapter.subject_id,
            'number_of_quizzes': len(quizzes),
            'quizzes': [{
                'id': q.id,
                'date': q.date_of_quiz,
                'duration': q.time_duration,
                'num_questions': len(q.questions)
            } for q in quizzes]
        }
        return jsonify(debug_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 