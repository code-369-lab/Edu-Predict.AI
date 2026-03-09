import joblib
import numpy as np
import pandas as pd
from src.data_preprocessing import DataPreprocessor

class StudentPredictor:
    def __init__(self, model_path='models/best_model.pkl'):
        self.model = None
        self.preprocessor = DataPreprocessor()
        
        # Fit the preprocessor with training data to avoid NotFittedError
        df = self.preprocessor.load_data()
        if df is not None:
            self.preprocessor.preprocess_pipeline(df, fit=True)
            
        self.load_model(model_path)
    
    def load_model(self, model_path):
        """Load trained model"""
        try:
            self.model = joblib.load(model_path)
            print(f"Model loaded successfully from {model_path}")
        except FileNotFoundError:
            print(f"Error: Model file {model_path} not found!")
            print("Please train a model first.")
    
    def prepare_input(self, student_data):
        """Prepare single student data for prediction"""
        # Create DataFrame from input
        df = pd.DataFrame([student_data])
        
        # Add dummy final_grade column (will be dropped)
        df['final_grade'] = 0
        
        # Preprocess
        X, _, _ = self.preprocessor.preprocess_pipeline(df, fit=False)
        
        return X
    
    def predict_grade(self, student_data):
        """Predict grade for a single student"""
        if self.model is None:
            return None, "Model not loaded"
        
        try:
            X = self.prepare_input(student_data)
            prediction = self.model.predict(X)[0]
            
            # Clip prediction to valid range
            prediction = np.clip(prediction, 0, 100)
            
            # Determine performance category
            if prediction < 50:
                category = "Poor"
            elif prediction < 70:
                category = "Average"
            elif prediction < 85:
                category = "Good"
            else:
                category = "Excellent"
            
            return prediction, category
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def get_recommendations(self, student_data, predicted_grade):
        """Get personalized recommendations with priority flags for UI badges."""
        recommendations = []
        
        if student_data['study_hours'] < 3:
            recommendations.append({"text": "📚 Increase study hours to at least 3-4 hours daily", "priority": "high"})
        
        if student_data['attendance'] < 80:
            recommendations.append({"text": "📅 Improve attendance - aim for at least 80%", "priority": "high"})
        
        if student_data['sleep_hours'] < 6:
            recommendations.append({"text": "😴 Get more sleep - aim for 7-8 hours per night", "priority": "medium"})
        elif student_data['sleep_hours'] > 9:
            recommendations.append({"text": "⏰ Balance sleep time - 7-8 hours is optimal", "priority": "low"})
        
        if not student_data['tutoring'] and predicted_grade < 70:
            recommendations.append({"text": "👨‍🏫 Consider getting tutoring support", "priority": "medium"})
        
        if not student_data['internet_access']:
            recommendations.append({"text": "🌐 Access to internet resources can help improve learning", "priority": "high"})
        
        if not student_data['extra_curricular']:
            recommendations.append({"text": "🎯 Participate in extra-curricular activities for holistic development", "priority": "low"})
        
        if not recommendations:
            recommendations.append({"text": "✅ Keep up the good work! Maintain your current study habits", "priority": "low"})
        
        return recommendations

if __name__ == "__main__":
    # Test prediction
    predictor = StudentPredictor()
    
    test_student = {
        'age': 18,
        'gender': 'M',
        'study_hours': 5.0,
        'attendance': 85.0,
        'previous_grade': 75.0,
        'parent_education': 'bachelor',
        'internet_access': 1,
        'family_support': 1,
        'extra_curricular': 1,
        'sleep_hours': 7.0,
        'tutoring': 0
    }
    
    grade, category = predictor.predict_grade(test_student)
    if grade:
        print(f"\nPredicted Grade: {grade:.2f}")
        print(f"Performance Category: {category}")
        
        recommendations = predictor.get_recommendations(test_student, grade)
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  {rec}")