import pandas as pd
import numpy as np
import os

def generate_student_data(n_samples=1000):
    """Generate synthetic student performance data"""
    np.random.seed(42)
    
    data = {
        'student_id': range(1, n_samples + 1),
        'age': np.random.randint(15, 25, n_samples),
        'gender': np.random.choice(['M', 'F'], n_samples),
        'study_hours': np.random.uniform(0, 10, n_samples),
        'attendance': np.random.uniform(50, 100, n_samples),
        'previous_grade': np.random.uniform(40, 100, n_samples),
        'parent_education': np.random.choice(['high_school', 'bachelor', 'master', 'phd'], n_samples),
        'internet_access': np.random.choice([0, 1], n_samples),
        'family_support': np.random.choice([0, 1], n_samples),
        'extra_curricular': np.random.choice([0, 1], n_samples),
        'sleep_hours': np.random.uniform(4, 10, n_samples),
        'tutoring': np.random.choice([0, 1], n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Generate final grade based on features with some noise
    df['final_grade'] = (
        df['study_hours'] * 5 +
        df['attendance'] * 0.3 +
        df['previous_grade'] * 0.4 +
        df['internet_access'] * 5 +
        df['family_support'] * 3 +
        df['tutoring'] * 4 +
        df['sleep_hours'] * 2 +
        np.random.normal(0, 5, n_samples)
    )
    
    # Normalize to 0-100 scale
    df['final_grade'] = np.clip(df['final_grade'], 0, 100)
    
    # Create performance category
    df['performance_category'] = pd.cut(
        df['final_grade'],
        bins=[0, 50, 70, 85, 100],
        labels=['Poor', 'Average', 'Good', 'Excellent']
    )
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/student_data.csv', index=False)
    print(f"Generated {n_samples} student records and saved to data/student_data.csv")
    return df

if __name__ == "__main__":
    generate_student_data(1000)