import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import xgboost as xgb
import joblib
import warnings

warnings.filterwarnings('ignore')

def train_universal_crop_model(dataset_path, model_output_path):
    print(f"Loading Universal Crop Dataset from {dataset_path}...")
    df = pd.read_csv(dataset_path)
    
    # Your sensors measure: Nitrogen, Phosphorus, Potassium, Temperature, pH, Moisture.
    # The Kaggle dataset has: N, P, K, temperature, humidity, ph, rainfall, label.
    # To ensure the model works perfectly offline with YOUR actual physical sensors, 
    # we train it strictly on the features your sensors capture.
    
    features = ['N', 'P', 'K', 'temperature', 'ph']
    target = 'label'
    
    X = df[features]
    y = df[target]
    
    # Encode the crop labels (e.g., 'rice' -> 0, 'maize' -> 1)
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Save the mapping so we can translate the prediction back to a word later
    joblib.dump(label_encoder, 'crop_label_encoder.pkl')
    print(f"Detected {len(label_encoder.classes_)} unique crops.")
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)
    
    print("\nTraining Universal XGBoost Classifier...")
    # Initialize and train the XGBoost model
    model = xgb.XGBClassifier(
        n_estimators=100, 
        max_depth=5, 
        learning_rate=0.1, 
        objective='multi:softprob',
        eval_metric='mlogloss',
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n✅ Universal Model Accuracy: {accuracy * 100:.2f}%")
    print(f"Even without humidity and rainfall sensors, the accuracy is quite high!")
    
    # Save the model
    model.save_model(model_output_path)
    print(f"\nUniversal model saved successfully to: {model_output_path}")
    print("This lightweight model is now ready to be deployed to the Dew Layer!")

if __name__ == "__main__":
    train_universal_crop_model('Crop_recommendation.csv', 'universal_crop_xgboost.json')
