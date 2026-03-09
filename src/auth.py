from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from src.models import db, User, Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard') if current_user.role == 'teacher' else url_for('index'))
        
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'success': True, 'redirect': url_for('dashboard') if user.role == 'teacher' else url_for('index')})
        else:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
         return redirect(url_for('dashboard') if current_user.role == 'teacher' else url_for('index'))
         
    if request.method == 'POST':
        data = request.json if request.is_json else request.form
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'student') # Default to student
        
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email already registered.'}), 400
            
        new_user = User(username=username, email=email, role=role)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # If student, create a blank student profile linked to them
        if role == 'student':
             new_student = Student(user_id=new_user.id, name=username, age=18, gender='M', parent_education='high_school')
             db.session.add(new_student)
             db.session.commit()
             
        login_user(new_user)
        return jsonify({'success': True, 'redirect': url_for('dashboard') if role == 'teacher' else url_for('index')})
        
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
