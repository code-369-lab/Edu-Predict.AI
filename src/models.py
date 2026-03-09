from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student') # 'student' or 'teacher'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Optional linking to a user account
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    parent_education = db.Column(db.String(50), nullable=False)
    
    # Static tracking properties (can change, but typically stable)
    internet_access = db.Column(db.Boolean, default=True)
    family_support = db.Column(db.Boolean, default=True)
    extra_curricular = db.Column(db.Boolean, default=True)
    tutoring = db.Column(db.Boolean, default=False)
    
    # Establish a relationship with activity logs and history
    activity_logs = db.relationship('ActivityLog', backref='student', lazy='dynamic')
    prediction_history = db.relationship('PredictionHistory', backref='student', lazy='dynamic')

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dynamic properties that change often (simulated in our stream)
    study_hours = db.Column(db.Float, nullable=False)
    attendance = db.Column(db.Float, nullable=False)
    sleep_hours = db.Column(db.Float, nullable=False)
    previous_grade = db.Column(db.Float, nullable=False)

class PredictionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    predicted_grade = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    
    # We can store recommendations as a JSON strong or simple serialized text
    recommendations = db.Column(db.Text, nullable=True) 
