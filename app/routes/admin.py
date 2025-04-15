from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.user import User
from app.models.score import Score
from app import db
from datetime import datetime
from functools import wraps
from sqlalchemy import func

bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics for dashboard
    total_users = User.query.filter_by(is_admin=False).count()
    total_subjects = Subject.query.count()
    total_quizzes = Quiz.query.count()
    
    # Get upcoming quizzes (quizzes with future dates)
    upcoming_quizzes = Quiz.query.filter(Quiz.date > datetime.now()).count()
    
    # Get recent users and scores
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    recent_scores = Score.query.order_by(Score.timestamp.desc()).limit(5).all()
    
    # Get all subjects for the overview section
    subjects = Subject.query.all()
    
    return render_template(
        'admin/dashboard.html',
        total_users=total_users,
        total_subjects=total_subjects,
        total_quizzes=total_quizzes,
        upcoming_quizzes=upcoming_quizzes,
        recent_users=recent_users,
        recent_scores=recent_scores,
        subjects=subjects
    )

@bp.route('/subjects', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_subjects():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        subject = Subject(name=name, description=description)
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('admin.manage_subjects'))
    
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)

@bp.route('/subjects/<int:subject_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Subject name is required!', 'danger')
            return redirect(url_for('admin.edit_subject', subject_id=subject_id))
        
        subject.name = name
        subject.description = description
        db.session.commit()
        flash('Subject updated successfully!', 'success')
        return redirect(url_for('admin.manage_subjects'))
    
    return render_template('admin/edit_subject.html', subject=subject)

@bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting subject. Make sure there are no associated chapters.', 'danger')
    
    return redirect(url_for('admin.manage_subjects'))

@bp.route('/subjects/<int:subject_id>/chapters', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        chapter = Chapter(name=name, description=description, subject_id=subject_id)
        db.session.add(chapter)
        db.session.commit()
        flash('Chapter added successfully!', 'success')
        return redirect(url_for('admin.manage_chapters', subject_id=subject_id))
    
    return render_template('admin/chapters.html', subject=subject)

@bp.route('/chapters/<int:chapter_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        if not name:
            flash('Chapter name is required!', 'danger')
            return redirect(url_for('admin.edit_chapter', chapter_id=chapter_id))
        
        chapter.name = name
        chapter.description = description
        db.session.commit()
        flash('Chapter updated successfully!', 'success')
        return redirect(url_for('admin.manage_chapters', subject_id=chapter.subject_id))
    
    return render_template('admin/edit_chapter.html', chapter=chapter)

@bp.route('/chapters/<int:chapter_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    subject_id = chapter.subject_id
    try:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting chapter. Make sure there are no associated quizzes.', 'danger')
    
    return redirect(url_for('admin.manage_chapters', subject_id=subject_id))

@bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    
    if request.method == 'POST':
        try:
            date = datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M')
            duration = int(request.form.get('duration'))
            remarks = request.form.get('remarks')
            
            existing_quiz = Quiz.query.filter_by(
                chapter_id=chapter_id,
                date=date
            ).first()
            
            if existing_quiz:
                flash('A quiz already exists for this date and time.', 'danger')
                return redirect(url_for('admin.manage_quizzes', chapter_id=chapter_id))
            
            quiz = Quiz(
                chapter_id=chapter_id,
                date=date,
                duration=duration,
                remarks=remarks
            )
            db.session.add(quiz)
            db.session.commit()
            flash('Quiz added successfully!', 'success')
            return redirect(url_for('admin.manage_quizzes', chapter_id=chapter_id))
            
        except ValueError:
            flash('Invalid date/time format.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Error creating quiz.', 'danger')
    
    return render_template('admin/quizzes.html', chapter=chapter, now=datetime.now())

@bp.route('/quizzes/<int:quiz_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        try:
            date = datetime.strptime(request.form.get('date'), '%Y-%m-%dT%H:%M')
            duration = int(request.form.get('duration'))
            remarks = request.form.get('remarks')
            
            existing_quiz = Quiz.query.filter(
                Quiz.chapter_id == quiz.chapter_id,
                Quiz.date == date,
                Quiz.id != quiz_id
            ).first()
            
            if existing_quiz:
                flash('A quiz already exists for this date and time.', 'danger')
                return redirect(url_for('admin.edit_quiz', quiz_id=quiz_id))
            
            quiz.date = date
            quiz.duration = duration
            quiz.remarks = remarks
            db.session.commit()
            flash('Quiz updated successfully!', 'success')
            return redirect(url_for('admin.manage_quizzes', chapter_id=quiz.chapter_id))
            
        except ValueError:
            flash('Invalid date/time format.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Error updating quiz.', 'danger')
    
    return render_template('admin/edit_quiz.html', quiz=quiz)

@bp.route('/quizzes/<int:quiz_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    chapter_id = quiz.chapter_id
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting quiz. Make sure there are no attempts.', 'danger')
    
    return redirect(url_for('admin.manage_quizzes', chapter_id=chapter_id))

@bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_questions(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if request.method == 'POST':
        question_statement = request.form.get('question_text')
        option1 = request.form.get('option_a')
        option2 = request.form.get('option_b')
        option3 = request.form.get('option_c')
        option4 = request.form.get('option_d')
        correct_option = request.form.get('correct_option')
        
        if not all([question_statement, option1, option2, option3, option4, correct_option]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))
        
        # Convert correct_option from a/b/c/d to 1/2/3/4
        correct_option_map = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        correct_option = correct_option_map.get(correct_option.lower(), 1)
        
        question = Question(
            quiz_id=quiz_id,
            question_statement=question_statement,
            option1=option1,
            option2=option2,
            option3=option3,
            option4=option4,
            correct_option=correct_option
        )
        db.session.add(question)
        db.session.commit()
        flash('Question added successfully!', 'success')
        return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))
    
    return render_template('admin/questions.html', quiz=quiz)

@bp.route('/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        question_statement = request.form.get('question_statement')
        option1 = request.form.get('option1')
        option2 = request.form.get('option2')
        option3 = request.form.get('option3')
        option4 = request.form.get('option4')
        correct_option = request.form.get('correct_option')
        
        if not all([question_statement, option1, option2, option3, option4, correct_option]):
            flash('All fields are required!', 'danger')
            return redirect(url_for('admin.edit_question', question_id=question_id))
        
        question.question_statement = question_statement
        question.option1 = option1
        question.option2 = option2
        question.option3 = option3
        question.option4 = option4
        question.correct_option = int(correct_option)
        
        db.session.commit()
        flash('Question updated successfully!', 'success')
        return redirect(url_for('admin.manage_questions', quiz_id=question.quiz_id))
    
    return render_template('admin/edit_question.html', question=question)

@bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting question.', 'danger')
    
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))

@bp.route('/search')
@login_required
@admin_required
def search():
    query = request.args.get('q', '').strip()
    type = request.args.get('type', 'all')
    
    if not query:
        return render_template('admin/search.html', results=None)
    
    results = {
        'users': [],
        'subjects': [],
        'chapters': [],
        'quizzes': []
    }
    
    if type in ['all', 'users']:
        results['users'] = User.query.filter(
            User.email.ilike(f'%{query}%') | 
            User.full_name.ilike(f'%{query}%')
        ).all()
    
    if type in ['all', 'subjects']:
        results['subjects'] = Subject.query.filter(
            Subject.name.ilike(f'%{query}%') |
            Subject.description.ilike(f'%{query}%')
        ).all()
    
    if type in ['all', 'chapters']:
        results['chapters'] = Chapter.query.filter(
            Chapter.name.ilike(f'%{query}%') |
            Chapter.description.ilike(f'%{query}%')
        ).all()
    
    if type in ['all', 'quizzes']:
        results['quizzes'] = Quiz.query.filter(
            Quiz.remarks.ilike(f'%{query}%')
        ).all()
    
    return render_template('admin/search.html', results=results, query=query, type=type)

@bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.filter_by(is_admin=False).all()
    return render_template('admin/users.html', users=users)

@bp.route('/api/subjects')
@login_required
@admin_required
def get_subjects():
    subjects = Subject.query.all()
    return jsonify([{
        'id': subject.id,
        'name': subject.name,
        'description': subject.description
    } for subject in subjects])

@bp.route('/api/chapters/<int:subject_id>')
@login_required
@admin_required
def get_chapters(subject_id):
    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return jsonify([{
        'id': chapter.id,
        'name': chapter.name,
        'description': chapter.description
    } for chapter in chapters])

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting admin users
    if user.is_admin:
        flash('Cannot delete admin users.', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting user. Make sure there are no associated quiz attempts.', 'danger')
    
    return redirect(url_for('admin.manage_users')) 