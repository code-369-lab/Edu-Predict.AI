import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.tree import DecisionTreeRegressor
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
import matplotlib.pyplot as plt
import seaborn as sns

class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_model_name = None
        self.results = {}
        
    def initialize_models(self):
        """Initialize different ML models"""
        self.models = {
            'Linear Regression': LinearRegression(),
            'Ridge Regression': Ridge(alpha=1.0),
            'Lasso Regression': Lasso(alpha=1.0),
            'Decision Tree': DecisionTreeRegressor(max_depth=10, random_state=42),
            'Random Forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42),
            'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
            'SVR': SVR(kernel='rbf', C=100, gamma=0.1)
        }
        print(f"Initialized {len(self.models)} models")
    
    def train_model(self, model_name, model, X_train, y_train):
        """Train a single model"""
        print(f"Training {model_name}...")
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(self, model, X_test, y_test):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        return {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2,
            'predictions': y_pred
        }
    
    def train_all_models(self, X_train, y_train, X_test, y_test):
        """Train and evaluate all models"""
        self.initialize_models()
        
        for name, model in self.models.items():
            # Train model
            trained_model = self.train_model(name, model, X_train, y_train)
            
            # Evaluate on test set
            metrics = self.evaluate_model(trained_model, X_test, y_test)
            
            self.results[name] = {
                'model': trained_model,
                'metrics': metrics
            }
            
            print(f"{name} - R2: {metrics['R2']:.4f}, RMSE: {metrics['RMSE']:.4f}, MAE: {metrics['MAE']:.4f}")
        
        # Find best model based on R2 score
        self.best_model_name = max(self.results, key=lambda x: self.results[x]['metrics']['R2'])
        self.best_model = self.results[self.best_model_name]['model']
        
        print(f"\nBest Model: {self.best_model_name}")
        return self.results
    
    def plot_results(self, y_test, save_path='models/'):
        """Plot model comparison and predictions"""
        os.makedirs(save_path, exist_ok=True)
        
        # Model comparison
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # R2 Score comparison
        r2_scores = {name: results['metrics']['R2'] for name, results in self.results.items()}
        axes[0, 0].bar(r2_scores.keys(), r2_scores.values(), color='skyblue')
        axes[0, 0].set_title('R2 Score Comparison', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('R2 Score')
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].grid(axis='y', alpha=0.3)
        
        # RMSE comparison
        rmse_scores = {name: results['metrics']['RMSE'] for name, results in self.results.items()}
        axes[0, 1].bar(rmse_scores.keys(), rmse_scores.values(), color='salmon')
        axes[0, 1].set_title('RMSE Comparison', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('RMSE')
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].grid(axis='y', alpha=0.3)
        
        # Best model predictions vs actual
        best_predictions = self.results[self.best_model_name]['metrics']['predictions']
        axes[1, 0].scatter(y_test, best_predictions, alpha=0.5)
        axes[1, 0].plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', lw=2)
        axes[1, 0].set_xlabel('Actual Grades')
        axes[1, 0].set_ylabel('Predicted Grades')
        axes[1, 0].set_title(f'Best Model ({self.best_model_name}) - Predictions vs Actual', 
                            fontsize=14, fontweight='bold')
        axes[1, 0].grid(alpha=0.3)
        
        # Error distribution
        errors = y_test - best_predictions
        axes[1, 1].hist(errors, bins=30, color='lightgreen', edgecolor='black')
        axes[1, 1].set_xlabel('Prediction Error')
        axes[1, 1].set_ylabel('Frequency')
        axes[1, 1].set_title('Error Distribution', fontsize=14, fontweight='bold')
        axes[1, 1].axvline(x=0, color='red', linestyle='--', linewidth=2)
        axes[1, 1].grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(os.path.join(save_path, 'model_comparison.png'), dpi=300, bbox_inches='tight')
        print(f"Model comparison plot saved to {save_path}")
        plt.close()
    
    def plot_feature_importance(self, feature_names, save_path='models/'):
        """Plot feature importance for tree-based models"""
        if self.best_model_name in ['Random Forest', 'Gradient Boosting', 'Decision Tree']:
            importances = self.best_model.feature_importances_
            indices = np.argsort(importances)[::-1]
            
            plt.figure(figsize=(12, 8))
            plt.title(f'Feature Importance - {self.best_model_name}', fontsize=16, fontweight='bold')
            plt.bar(range(len(importances)), importances[indices], color='teal')
            plt.xticks(range(len(importances)), [feature_names[i] for i in indices], rotation=45, ha='right')
            plt.ylabel('Importance')
            plt.xlabel('Features')
            plt.grid(axis='y', alpha=0.3)
            plt.tight_layout()
            plt.savefig(os.path.join(save_path, 'feature_importance.png'), dpi=300, bbox_inches='tight')
            print(f"Feature importance plot saved to {save_path}")
            plt.close()
    
    def save_best_model(self, filepath='models/best_model.pkl'):
        """Save the best model to disk"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.best_model, filepath)
        print(f"Best model ({self.best_model_name}) saved to {filepath}")
    
    def save_results_report(self, filepath='models/results_report.txt'):
        """Save detailed results report"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write("="*60 + "\n")
            f.write("STUDENT PERFORMANCE PREDICTION - MODEL EVALUATION REPORT\n")
            f.write("="*60 + "\n\n")
            
            for name, result in self.results.items():
                f.write(f"\n{name}\n")
                f.write("-"*40 + "\n")
                for metric, value in result['metrics'].items():
                    if metric != 'predictions':
                        f.write(f"{metric}: {value:.4f}\n")
                f.write("\n")
            
            f.write("="*60 + "\n")
            f.write(f"BEST MODEL: {self.best_model_name}\n")
            f.write("="*60 + "\n")
        
        print(f"Results report saved to {filepath}")

if __name__ == "__main__":
    from data_preprocessing import DataPreprocessor
    
    # Load and preprocess data
    preprocessor = DataPreprocessor()
    df = preprocessor.load_data()
    
    if df is not None:
        X, y, feature_names = preprocessor.preprocess_pipeline(df)
        X_train, X_test, y_train, y_test = preprocessor.get_train_test_split(X, y)
        
        # Train models
        trainer = ModelTrainer()
        results = trainer.train_all_models(X_train, y_train, X_test, y_test)
        
        # Plot results
        trainer.plot_results(y_test)
        trainer.plot_feature_importance(feature_names)
        
        # Save model and results
        trainer.save_best_model()
        trainer.save_results_report()