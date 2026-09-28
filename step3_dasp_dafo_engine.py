import pandas as pd
import hashlib
import json
import os
import xgboost as xgb
import joblib
from ecdsa import SigningKey, SECP256k1
import warnings

warnings.filterwarnings('ignore')

# Generate or load ECDSA keys for the Dew Node (Edge device)
if not os.path.exists("private.pem"):
    private_key = SigningKey.generate(curve=SECP256k1)
    with open("private.pem", "wb") as f:
        f.write(private_key.to_pem())
    public_key = private_key.get_verifying_key()
    with open("public.pem", "wb") as f:
        f.write(public_key.to_pem())
else:
    with open("private.pem", "rb") as f:
        private_key = SigningKey.from_pem(f.read())

def create_hash_chain_predict_and_sign(input_csv, buffer_file, model_file, encoder_file):
    print("Loading sensor data stream...")
    df = pd.read_csv(input_csv)
    
    print("Loading Machine Learning Model for Local Edge Inference...")
    # Load the trained XGBoost model and the label encoder
    model = xgb.XGBClassifier()
    model.load_model(model_file)
    label_encoder = joblib.load(encoder_file)
    
    # DASP-DAFO Weights
    alpha = 0.5  # Criticality weight
    gamma = 0.2  # Quality weight

    buffer = []
    previous_hash = "0" * 64 # Initial Genesis Hash (Blockchain root)
    
    print("Starting DASP-DAFO Edge Engine: Predicting -> Hashing -> Signing...")
    for index, row in df.iterrows():
        # --- 1. LOCAL ML INFERENCE (Crop & Irrigation Prediction) ---
        # Get live sensor features
        features = pd.DataFrame([{
            'N': row['Nitrogen'], 
            'P': row['Phosphorus'], 
            'K': row['Potassium'], 
            'temperature': row['Temperature'], 
            'ph': row['pH']
        }])
        
        # Predict Crop using the XGBoost model we trained in Step 2
        crop_encoded = model.predict(features)[0]
        predicted_crop = label_encoder.inverse_transform([crop_encoded])[0]
        
        # Predict Irrigation (Rule-based controller based on Moisture)
        predicted_irrigation = bool(row['Moisture'] < 50)
        calculated_criticality = 0.9 if predicted_irrigation else 0.2
        
        # --- 2. BASE PACKET CREATION ---
        packet_data = {
            "device_id": "NODE_01",
            "seq": int(row['entry_id']),
            "timestamp": row['created_at'],
            "Nitrogen": row['Nitrogen'],
            "Phosphorus": row['Phosphorus'],
            "Potassium": row['Potassium'],
            "Temperature": row['Temperature'],
            "Moisture": row['Moisture'],
            "pH": row['pH'],
            "Quality": row['Quality'],
            # The ML Predictions are added to the packet!
            "Predicted_Irrigation": predicted_irrigation,
            "Predicted_Crop": predicted_crop,
            "Criticality": calculated_criticality
        }
        
        # --- 3. DASP-DAFO Priority ---
        priority = (alpha * calculated_criticality) + (gamma * row['Quality'])
        packet_data["Priority"] = priority
        
        # --- 4. BLOCKCHAIN CRYPTOGRAPHY (Hashing & Signing before upload) ---
        packet_data["previous_hash"] = previous_hash
        packet_string = json.dumps(packet_data, sort_keys=True).encode('utf-8')
        
        # SHA-256 Hash Chaining (Blockchain block link)
        current_hash = hashlib.sha256(packet_string).hexdigest()
        
        # ECDSA Digital Signature (Proves the Dew Node created this block)
        signature = private_key.sign(packet_string).hex()
        
        final_packet = packet_data.copy()
        final_packet["hash"] = current_hash
        final_packet["signature"] = signature
        final_packet["sync_status"] = "pending_blockchain_upload"
        
        buffer.append(final_packet)
        previous_hash = current_hash
        
        if index % 500 == 0 and index > 0:
            print(f"Predicted and Secured {index} records...")
            
    print(f"Saving {len(buffer)} secured & predicted packets to offline buffer ({buffer_file})...")
    with open(buffer_file, 'w') as f:
        for packet in buffer:
            f.write(json.dumps(packet) + "\n")
            
    print("DASP-DAFO Edge Engine complete! Data is verified and ready for Blockchain/Cloud upload.")

if __name__ == "__main__":
    input_csv = "enriched_sensor_data.csv"
    buffer_file = "dew_local_buffer.jsonl"
    model_file = "universal_crop_xgboost.json"
    encoder_file = "crop_label_encoder.pkl"
    create_hash_chain_predict_and_sign(input_csv, buffer_file, model_file, encoder_file)
