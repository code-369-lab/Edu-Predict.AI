import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split

class DataPreprocessor:
    def __init__(self):
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        
    def load_data(self, filepath='data/student_data.csv'):
        """Load student data from CSV"""
        try:
            df = pd.read_csv(filepath)
            print(f"Data loaded successfully: {df.shape[0]} records, {df.shape[1]} features")
            return df
        except FileNotFoundError:
            print(f"Error: File {filepath} not found!")
            return None
    
    def handle_missing_values(self, df):
        """Handle missing values in the dataset"""
        # Fill numeric columns with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
        
        # Fill categorical columns with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode()[0])
        
        return df
    
    def encode_categorical_features(self, df, fit=True):
        """Encode categorical variables"""
        categorical_cols = ['gender', 'parent_education', 'performance_category']
        
        for col in categorical_cols:
            if col in df.columns:
                if fit:
                    self.label_encoders[col] = LabelEncoder()
                    df[col] = self.label_encoders[col].fit_transform(df[col])
                else:
                    if col in self.label_encoders:
                        df[col] = self.label_encoders[col].transform(df[col])
        
        return df
    
    def engineer_features(self, df):
        """Create new features"""
        # Study efficiency (study hours per grade point)
        df['study_efficiency'] = df['study_hours'] / (df['previous_grade'] + 1)
        
        # Total support (family + tutoring + internet)
        df['total_support'] = df['family_support'] + df['tutoring'] + df['internet_access']
        
        # Age-grade interaction
        df['age_grade_interaction'] = df['age'] * df['previous_grade']
        
        # Study-sleep balance
        df['study_sleep_balance'] = df['study_hours'] / (df['sleep_hours'] + 1)
        
        return df
    
    def prepare_features(self, df, target_col='final_grade', fit=True):
        """Prepare features for modeling"""
        # Drop unnecessary columns
        cols_to_drop = ['student_id', 'performance_category', target_col]
        X = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
        
        # Store feature names
        if fit:
            self.feature_names = X.columns.tolist()
        
        # Scale features
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        # Get target variable
        y = df[target_col] if target_col in df.columns else None
        
        return X_scaled, y, self.feature_names
    
    def preprocess_pipeline(self, df, target_col='final_grade', fit=True):
        """Complete preprocessing pipeline"""
        df = df.copy()
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Encode categorical features
        df = self.encode_categorical_features(df, fit=fit)
        
        # Engineer features
        df = self.engineer_features(df)
        
        # Prepare features
        X, y, feature_names = self.prepare_features(df, target_col, fit=fit)
        
        return X, y, feature_names
    
    def get_train_test_split(self, X, y, test_size=0.2, random_state=42):
        """Split data into training and testing sets"""
        return train_test_split(X, y, test_size=test_size, random_state=random_state)

if __name__ == "__main__":
    # Test preprocessing
    preprocessor = DataPreprocessor()
    df = preprocessor.load_data()
    
    if df is not None:
        X, y, feature_names = preprocessor.preprocess_pipeline(df)
        print(f"\nPreprocessed data shape: X={X.shape}, y={y.shape}")
        print(f"Feature names: {feature_names}")