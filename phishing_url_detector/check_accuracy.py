import joblib
import os

def check_accuracy():
    model_info_path = 'models/model_info.pkl'
    if os.path.exists(model_info_path):
        try:
            info = joblib.load(model_info_path)
            print("URL Model Performance (from last training):")
            print(f"Accuracy: {info.get('accuracy', 'N/A')}")
            print(f"Precision: {info.get('precision', 'N/A')}")
            print(f"Recall: {info.get('recall', 'N/A')}")
            print(f"F1 Score: {info.get('f1_score', 'N/A')}")
        except Exception as e:
            print(f"Error loading model info: {e}")
    else:
        print("Model info file not found. The model might not have been trained yet.")

if __name__ == "__main__":
    check_accuracy()
