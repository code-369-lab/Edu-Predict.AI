import time
import random
import threading
from app import app, db, socketio, predictor
from src.models import Student, ActivityLog, PredictionHistory

def stream_student_data():
    """
    Background process that continuously simulates incoming 
    data for existing students and emits WebSockets.
    """
    with app.app_context():
        print("Started real-time data streaming simulator...")
        
        # Give the server a moment to start
        time.sleep(2)
        
        while True:
            # Get a random student
            students = Student.query.all()
            if not students:
                time.sleep(5)
                continue
                
            student = random.choice(students)
            
            # Simulate a realistic fluctuation in their activities
            # E.g., attendance might drop, study hours fluctuate daily
            last_log = ActivityLog.query.filter_by(student_id=student.id).order_by(ActivityLog.timestamp.desc()).first()
            
            if last_log:
                new_attendance = max(0, min(100, last_log.attendance + random.uniform(-5, 2)))
                new_study = max(0, min(24, last_log.study_hours + random.uniform(-1, 1)))
                new_sleep = max(0, min(24, last_log.sleep_hours + random.uniform(-1, 1)))
                prev_grade = last_log.previous_grade
            else:
                # Baseline
                new_attendance = random.uniform(50, 100)
                new_study = random.uniform(0, 10)
                new_sleep = random.uniform(4, 10)
                prev_grade = random.uniform(40, 100)
                
            # Log the new activity
            new_log = ActivityLog(
                student_id=student.id,
                study_hours=new_study,
                attendance=new_attendance,
                sleep_hours=new_sleep,
                previous_grade=prev_grade
            )
            db.session.add(new_log)
            
            # Formulate prediction input combining static and dynamic traits
            student_data = {
                'age': student.age,
                'gender': student.gender,
                'study_hours': new_study,
                'attendance': new_attendance,
                'previous_grade': prev_grade,
                'parent_education': student.parent_education,
                'internet_access': int(student.internet_access),
                'family_support': int(student.family_support),
                'extra_curricular': int(student.extra_curricular),
                'sleep_hours': new_sleep,
                'tutoring': int(student.tutoring)
            }
            
            # Run the ML Prediction instantly
            if predictor and predictor.model:
                grade, category = predictor.predict_grade(student_data)
                
                # Check for prediction success
                if grade is not None:
                    # Save to DB
                    history = PredictionHistory(
                        student_id=student.id,
                        predicted_grade=grade,
                        category=category
                    )
                    db.session.add(history)
                    db.session.commit()
                    
                    # Emit live update via WebSocket
                    update_payload = {
                        'student_id': student.id,
                        'name': student.name,
                        'attendance': round(new_attendance, 1),
                        'study_hours': round(new_study, 1),
                        'predicted_grade': round(float(grade), 1),
                        'category': category,
                        'is_alert': category == "Poor"
                    }
                    socketio.emit('student_update', update_payload)
                    
                    if category == "Poor":
                         print(f"⚠️ ALERT: Student {student.name} is At-Risk! (Grade: {grade:.1f}%)")
            else:
                 # Just commit the activity log if predictor fails
                 db.session.commit()
                 
            # Wait a few seconds before generating the next event
            time.sleep(random.uniform(2, 5))

def start_streamer():
    """Start the background streaming thread"""
    thread = threading.Thread(target=stream_student_data, daemon=True)
    thread.start()
    return thread
