from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    full_name = db.Column(db.String(100), nullable=False)
    qualification = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    login_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    scores = db.relationship('Score', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_login_timestamp(self):
        self.last_login = datetime.utcnow()
        self.login_attempts = 0
        db.session.commit()

    def increment_login_attempt(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:  # Lock account after 5 failed attempts
            self.is_locked = True
        db.session.commit()

    def unlock_account(self):
        self.is_locked = False
        self.login_attempts = 0
        db.session.commit()

    def __repr__(self):
        return f'<User {self.email}>' 