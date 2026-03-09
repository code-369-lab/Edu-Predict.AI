import os
import sys

def setup_project():
    """Setup project directories"""
    directories = ['data', 'models', 'src']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

def run_complete_pipeline():
    """Run the complete ML pipeline"""
    print("="*60)
    print("STUDENT PERFORMANCE PREDICTION SYSTEM")
    print("="*60)
    
    # Setup
    print("\n1. Setting up project structure...")
    setup_project()
    
    # Generate data
    print("\n2. Generating sample data...")
    from data_generator import generate_student_data
    df = generate_student_data(1000)
    
    # Preprocess data
    print("\n3. Preprocessing data...")
    from src.data_preprocessing import DataPreprocessor
    preprocessor = DataPreprocessor()
    df = preprocessor.load_data()
    X, y, feature_names = preprocessor.preprocess_pipeline(df)
    X_train, X_test, y_train, y_test = preprocessor.get_train_test_split(X, y)
    
    # Train models
    print("\n4. Training machine learning models...")
    from src.model_training import ModelTrainer
    trainer = ModelTrainer()
    results = trainer.train_all_models(X_train, y_train, X_test, y_test)
    
    # Generate visualizations
    print("\n5. Generating visualizations...")
    trainer.plot_results(y_test)
    trainer.plot_feature_importance(feature_names)
    
    # Save model and results
    print("\n6. Saving model and results...")
    trainer.save_best_model()
    trainer.save_results_report()
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\nBest Model: {trainer.best_model_name}")
    print(f"R2 Score: {trainer.results[trainer.best_model_name]['metrics']['R2']:.4f}")
    print(f"RMSE: {trainer.results[trainer.best_model_name]['metrics']['RMSE']:.4f}")
    print("\nModel saved to: models/best_model.pkl")
    print("Results saved to: models/results_report.txt")
    print("Visualizations saved to: models/")

def run_gui():
    """Launch GUI application"""
    print("\nLaunching GUI application...")
    from src.gui import StudentPerformanceGUI
    
    gui = StudentPerformanceGUI()
    gui.run()

if __name__ == "__main__":
    print("Student Performance Prediction System")
    print("\nOptions:")
    print("1. Run complete ML pipeline (train models)")
    print("2. Launch old GUI application")
    print("3. Run both")
    print("4. Launch Web Application (Web UI)")
    
    choice = input("\nEnter your choice (1/2/3/4): ").strip()
    
    if choice == '1':
        run_complete_pipeline()
    elif choice == '2':
        run_gui()
    elif choice == '3':
        run_complete_pipeline()
        print("\n" + "="*60)
        input("Press Enter to launch GUI...")
        run_gui()
    elif choice == '4':
        print("\nLaunching Flask Web Server...")
        from app import run_server
        run_server()
    else:
        print("Invalid choice!")