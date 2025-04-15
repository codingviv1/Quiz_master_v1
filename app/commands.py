from flask.cli import with_appcontext
import click
from app import db
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.subject import Subject
from app.models.chapter import Chapter
from app.models.user import User
from datetime import datetime, timedelta

@click.command('create-admin')
@with_appcontext
def create_admin():
    """Create an admin user."""
    try:
        admin = User(
            email='admin@example.com',
            full_name='Admin User',
            qualification='Administrator',
            date_of_birth=datetime.now().date(),
            is_admin=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created successfully!")
        print("Email: admin@example.com")
        print("Password: admin123")

    except Exception as e:
        db.session.rollback()
        print(f"Error creating admin user: {str(e)}")

@click.command('create-sample-data')
@with_appcontext
def create_sample_data():
    """Create sample subjects and chapters for testing."""
    try:
        # Create sample subjects
        subjects_data = [
            {
                'name': 'Mathematics',
                'description': 'Basic to advanced mathematics concepts',
                'chapters': [
                    {'name': 'Algebra', 'description': 'Basic algebraic concepts'},
                    {'name': 'Geometry', 'description': 'Basic geometric principles'},
                    {'name': 'Calculus', 'description': 'Introduction to calculus'}
                ]
            },
            {
                'name': 'Physics',
                'description': 'Fundamental physics concepts',
                'chapters': [
                    {'name': 'Mechanics', 'description': 'Basic mechanics and motion'},
                    {'name': 'Thermodynamics', 'description': 'Heat and energy'},
                    {'name': 'Optics', 'description': 'Light and optical phenomena'}
                ]
            }
        ]

        for subject_data in subjects_data:
            subject = Subject(
                name=subject_data['name'],
                description=subject_data['description']
            )
            db.session.add(subject)
            db.session.flush()  # To get the subject ID

            for chapter_data in subject_data['chapters']:
                chapter = Chapter(
                    name=chapter_data['name'],
                    description=chapter_data['description'],
                    subject_id=subject.id
                )
                db.session.add(chapter)

        db.session.commit()
        print("Sample subjects and chapters created successfully!")

    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample data: {str(e)}")

@click.command('create-sample-quizzes')
@with_appcontext
def create_sample_quizzes():
    """Create sample quizzes for testing."""
    try:
        # Create a quiz for each chapter
        from app.models.chapter import Chapter
        chapters = Chapter.query.all()
        
        for chapter in chapters:
            # Create a quiz
            quiz = Quiz(
                chapter_id=chapter.id,
                date_of_quiz=datetime.now() + timedelta(days=7),  # Set to 7 days from now
                time_duration="00:30",  # 30 minutes
                remarks="Sample quiz for testing"
            )
            db.session.add(quiz)
            db.session.flush()  # To get the quiz ID
            
            # Create 5 sample questions for each quiz
            for i in range(5):
                question = Question(
                    quiz_id=quiz.id,
                    question_statement=f"Sample question {i+1} for {chapter.name}",
                    option1="Option 1",
                    option2="Option 2",
                    option3="Option 3",
                    option4="Option 4",
                    correct_option=1  # First option is correct
                )
                db.session.add(question)
            
            print(f"Created quiz for chapter: {chapter.name}")
        
        db.session.commit()
        print("Sample quizzes created successfully!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating sample quizzes: {str(e)}")

def init_app(app):
    app.cli.add_command(create_admin)
    app.cli.add_command(create_sample_data)
    app.cli.add_command(create_sample_quizzes) 