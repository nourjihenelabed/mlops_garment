from model_pipeline import *
import argparse
import joblib
import os 
def main():
    parser = argparse.ArgumentParser(description='Garment Productivity Prediction Pipeline')
    parser.add_argument('--prepare', action='store_true', help='Only prepare data')
    parser.add_argument('--train', action='store_true', help='Only train model')
    parser.add_argument('--evaluate', action='store_true', help='Only evaluate model')
    parser.add_argument('--all', action='store_true', help='Run complete pipeline (default)')
    parser.add_argument('--data_path', type=str, default='dataProductivity-Prediction-of-Garment-Employeese.csv', help='Path to the dataset CSV file')
    
    args = parser.parse_args()
    
    # If no arguments provided, run everything
    if not any([args.prepare, args.train, args.evaluate, args.all]):
        args.all = True
    
    print("Starting Garment Productivity Prediction Pipeline...")
    print(f"Using dataset from: {args.data_path}")

    if args.prepare or args.all:
        print("\nSTEP 1: Preparing Data...")
        # Step 1: Load data
        df = load_data(args.data_path)
        
        # Step 2: Explore data
        explore_data(df)
        
        # Step 3: Clean data
        df_clean = clean_data(df)
        
        # Step 4: Engineer features
        df_featured = engineer_features(df_clean)
        
        # Step 5: Prepare data for training
        X_train, X_test, y_train, y_test, preprocessor = prepare_data(df_featured)
        
        # Save prepared data for later use
        joblib.dump({'X_train': X_train, 'X_test': X_test, 'y_train': y_train, 'y_test': y_test, 'preprocessor': preprocessor}, 
                   'prepared_data.joblib')
        print("Data preparation completed and saved!")
    
    if args.train or args.all:
        print("\nSTEP 2: Training Model...")
        # Load prepared data
        try:
            data = joblib.load('prepared_data.joblib')
            X_train, X_test, y_train, y_test, preprocessor = data['X_train'], data['X_test'], data['y_train'], data['y_test'], data['preprocessor']
        except:
            print("No prepared data found. Please run --prepare first.")
            return
        
        # Train AdaBoost model
        model = train_model(X_train, y_train, preprocessor)
        
        # Save the model
        save_model(model, 'tuned_ada_productivity_model.pkl')
        print("Model training completed!")
    
    if args.evaluate or args.all:
        print("\nSTEP 3: Evaluating Model...")
        # Load model and data
        try:
            model = load_model('tuned_ada_productivity_model.pkl')
            data = joblib.load('prepared_data.joblib')
            X_test, y_test = data['X_test'], data['y_test']
        except:
            print("Model or data not found. Please run --train first.")
            return
        
        # Evaluate model
        results = evaluate_model(model, X_test, y_test)
        
        print("Model Evaluation Results:")
        print(f"RMSE: {results['rmse']:.4f}")
        print(f"MAE: {results['mae']:.4f}")
        print(f"R2: {results['r2']:.4f}")
        print("Model evaluation completed!")
    
    print("\nPipeline completed successfully!")

if __name__ == "__main__":
    main()
