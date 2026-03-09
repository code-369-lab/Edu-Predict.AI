from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, login_required, current_user
from src.models import db, User, Student, ActivityLog, PredictionHistory
import sys
import os

# Ensure the src directory is in the path so we can import the predictor
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.prediction import StudentPredictor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-123' # To be moved to env vars later
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///edupredict.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
from src.auth import auth_bp
app.register_blueprint(auth_bp)

# Ensure database tables exist before first request
with app.app_context():
    db.create_all()
    
    # Create some mock students if the database is empty
    if not Student.query.first():
        print("Populating database with mock students...")
        mock_students = [
            Student(name="Alice Johnson", age=18, gender='F', parent_education="bachelor", internet_access=True, family_support=True, extra_curricular=True, tutoring=False),
            Student(name="Bob Smith", age=19, gender='M', parent_education="high_school", internet_access=True, family_support=False, extra_curricular=False, tutoring=True),
            Student(name="Charlie Davis", age=18, gender='M', parent_education="master", internet_access=True, family_support=True, extra_curricular=True, tutoring=False),
            Student(name="Diana Prince", age=17, gender='F', parent_education="phd", internet_access=True, family_support=True, extra_curricular=True, tutoring=True),
            Student(name="Evan Wright", age=19, gender='M', parent_education="high_school", internet_access=False, family_support=False, extra_curricular=False, tutoring=False)
        ]
        db.session.bulk_save_objects(mock_students)
        db.session.commit()

# Initialize the predictor globally so it loads the model once at startup
try:
    predictor = StudentPredictor()
    
    # Import and start the background data streamer
    from src.data_streamer import start_streamer
    start_streamer()
    
except Exception as e:
    print(f"Warning: Could not initialize predictor. {e}")
    predictor = None

@app.route('/')
@login_required
def index():
    """Serve the main HTML interface."""
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    """Serve the Live Streaming Teacher Dashboard."""
    if current_user.role != 'teacher':
        return redirect(url_for('index'))
    return render_template('dashboard.html')


@app.route('/study')
@login_required
def study_assistant():
    """AI Study Assistant Portal for Students."""
    return render_template('study.html')


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    """API endpoint to receive student data and return predictions."""
    if not predictor or predictor.model is None:
        return jsonify({
            'success': False, 
            'error': 'Machine learning model is not loaded. Please train the model first.'
        }), 500

    try:
        # Get JSON data from request
        data = request.json
        
        # Prepare the student data dictionary with correct types
        student_data = {
            'age': int(data.get('age', 18)),
            'gender': data.get('gender', 'M'),
            'study_hours': float(data.get('study_hours', 0)),
            'attendance': float(data.get('attendance', 0)),
            'previous_grade': float(data.get('previous_grade', 0)),
            'parent_education': data.get('parent_education', 'high_school'),
            'internet_access': int(data.get('internet_access', 0)),
            'family_support': int(data.get('family_support', 0)),
            'extra_curricular': int(data.get('extra_curricular', 0)),
            'sleep_hours': float(data.get('sleep_hours', 0)),
            'tutoring': int(data.get('tutoring', 0))
        }

        # Predict the grade and category
        grade, category = predictor.predict_grade(student_data)
        
        if grade is None:
             return jsonify({'success': False, 'error': category}), 500

        # Get recommendations
        recommendations = predictor.get_recommendations(student_data, grade)
        
        # Explainable AI (XAI) feature importance 
        # (Using a simple heuristic relative calculation as a placeholder for full SHAP)
        xai_impacts = {
            "Attendance": round(((student_data['attendance'] - 50) / 100) * 20, 1),
            "Study Hours": round(((student_data['study_hours'] - 5) / 15) * 15, 1),
            "Previous Grade": round(((student_data['previous_grade'] - 50) / 100) * 25, 1),
            "Sleep Quality": round((1 if 7 <= student_data['sleep_hours'] <= 9 else -1) * 5, 1)
        }
        
        # Sort by absolute impact impact and take top 3
        top_impacts = dict(sorted(xai_impacts.items(), key=lambda item: abs(item[1]), reverse=True)[:3])

        return jsonify({
            'success': True,
            'grade': round(float(grade), 2),
            'category': category,
            'recommendations': recommendations,
            'xai': top_impacts
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

import json
@app.route('/save_prediction', methods=['POST'])
@login_required
def save_prediction():
    """Save user prediction to history."""
    try:
        data = request.json
        student = Student.query.filter_by(user_id=current_user.id).first()
        
        if not student:
            return jsonify({'success': False, 'error': 'No student profile linked.'}), 400

        # Log Activity
        new_activity = ActivityLog(
            student_id=student.id,
            study_hours=float(data.get('study_hours', 0)),
            attendance=float(data.get('attendance', 0)),
            sleep_hours=float(data.get('sleep_hours', 0)),
            previous_grade=float(data.get('previous_grade', 0))
        )
        db.session.add(new_activity)
        db.session.flush()

        # Save History
        prediction_log = PredictionHistory(
            student_id=student.id,
            predicted_grade=float(data.get('predicted_grade', 0)),
            category=data.get('category', 'Unknown'),
            recommendations=json.dumps(data.get('recommendations', []))
        )
        db.session.add(prediction_log)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Online Backend Chat Handler. Optionally hook this to an OpenAI endpoint in production."""
    user_message = request.form.get('message', '').lower()
    
    # -------------------------------------------------------------
    # Simulated "Online" Backend NLP Engine
    # (In a real scenario, this would be an API call to a massive LLM)
    # -------------------------------------------------------------
    
    response_text = "I'm the cloud-hosted EduPredict AI! ☁️ I didn't quite catch that. Want to know how your predictions are calculated?"
    
    if "hello" in user_message or "hi" in user_message:
        response_text = "Welcome to the EduPredict.AI Cloud Server! How can I assist you with your predictions today?"
    elif "improve" in user_message or "help" in user_message:
        response_text = "Based on aggregate multi-tenant models, the fastest way to boost an 'Average' score is consistently logging over 7 hours of sleep and participating in at least one extracurricular activity!"
    elif "model" in user_message or "algorithm" in user_message:
        response_text = "The prediction engine uses a Random Forest Classifier trained on thousands of student data points via Scikit-Learn. It's hosted right here on this server."
        
    return jsonify({'reply': response_text})


@app.route('/api/study', methods=['POST'])
@login_required
def api_study_generate():
    """Generate dynamic study materials based on user topic."""
    data = request.json
    topic = data.get('topic', 'General Studies').title()
    
    # -------------------------------------------------------------
    # Simulated "AI" Structured Response Engine
    # (Maps to OpenAI Structured Outputs or LangChain in Prod)
    # -------------------------------------------------------------
    import random
    
    # Mock knowledge generation based on string hashing for consistency
    seed = sum(ord(c) for c in topic)
    random.seed(seed)
    
    study_plan = {
        "topic": topic,
        "summary": f"Your personalized curriculum for {topic}. Mastering this requires breaking down the core principles, engaging in active recall, and structuring your time efficiently.",
        "difficulty": random.choice(["Beginner", "Intermediate", "Advanced"]),
        "flashcards": [
            {
                "front": f"What is the core definition of {topic}?",
                "back": f"{topic} involves the systematic study and application of its fundamental laws and methodologies."
            },
            {
                "front": f"Name a primary application of {topic}.",
                "back": "It is widely used in modern industry to solve complex optimization problems."
            },
            {
                "front": f"Who are the key figures associated with {topic}?",
                "back": "Historically, pioneers in this field laid the groundwork through extensive empirical research."
            }
        ],
        "schedule": [
            {"day": "Day 1-2", "task": f"Introduction and Background Reading on {topic}."},
            {"day": "Day 3-4", "task": "Active Flashcard Review & Concept Mapping."},
            {"day": "Day 5-6", "task": "Practical Application problems and Quiz."},
            {"day": "Day 7", "task": "Mock Exam & Review of weak areas."}
        ]
    }
    
    return jsonify({'success': True, 'material': study_plan})


def run_server(port=5000):
    """Run the Flask development server with SocketIO."""
    print(f"Starting server on port {port}...")
    socketio.run(app, debug=True, port=port, use_reloader=False)

if __name__ == '__main__':
    run_server()
