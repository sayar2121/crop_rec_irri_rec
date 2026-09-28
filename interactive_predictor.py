import pandas as pd
import xgboost as xgb
import joblib
import warnings

warnings.filterwarnings('ignore')

def predict_from_sensors(N, P, K, temp, ph, moisture):
    # Load the trained ML model and label encoder
    try:
        model = xgb.XGBClassifier()
        model.load_model("universal_crop_xgboost.json")
        label_encoder = joblib.load("crop_label_encoder.pkl")
    except Exception as e:
        print("Error loading model. Did you run step2_train_models.py?")
        return
    
    # 1. Predict the Crop
    features = pd.DataFrame([{
        'N': N, 
        'P': P, 
        'K': K, 
        'temperature': temp, 
        'ph': ph
    }])
    crop_encoded = model.predict(features)[0]
    predicted_crop = label_encoder.inverse_transform([crop_encoded])[0]
    
    # 2. Predict Irrigation Needs
    # (Based on our Dew Node logic: if moisture is below 50, it triggers an alert)
    irrigation_needed = moisture < 50
    
    # --- Display the Results ---
    print("\n" + "="*40)
    print("🌱 CURRENT SENSOR READINGS")
    print("="*40)
    print(f"Nitrogen (N):   {N}")
    print(f"Phosphorus (P): {P}")
    print(f"Potassium (K):  {K}")
    print(f"Temperature:    {temp} °C")
    print(f"pH Level:       {ph}")
    print(f"Moisture:       {moisture} %")
    
    print("\n" + "="*40)
    print("🎯 DASP-DAFO AI PREDICTION")
    print("="*40)
    print(f"🌾 Recommended Crop:    {predicted_crop.upper()}")
    
    if irrigation_needed:
        print(f"💧 Irrigation Status:   🚨 URGENT: WATER NEEDED!")
    else:
        print(f"💧 Irrigation Status:   ✅ NORMAL: Soil is moist")
    print("="*40 + "\n")

if __name__ == "__main__":
    print("Welcome to the DASP-DAFO Interactive Predictor!")
    print("Enter mock sensor values to test the Artificial Intelligence:\n")
    try:
        n = float(input("Enter Nitrogen (N) level (e.g., 90): "))
        p = float(input("Enter Phosphorus (P) level (e.g., 42): "))
        k = float(input("Enter Potassium (K) level (e.g., 43): "))
        t = float(input("Enter Temperature in °C (e.g., 20.8): "))
        ph = float(input("Enter pH level (e.g., 6.5): "))
        m = float(input("Enter Moisture % (e.g., 82): "))
        
        predict_from_sensors(n, p, k, t, ph, m)
        
    except ValueError:
        print("\nError: Please enter valid numbers only.")
    except KeyboardInterrupt:
        print("\nExiting predictor.")
