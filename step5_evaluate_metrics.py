import pandas as pd
import hashlib
import json
import time
import os
import xgboost as xgb
import joblib
from ecdsa import SigningKey, VerifyingKey, SECP256k1
import warnings

warnings.filterwarnings('ignore')

def evaluate_metrics(input_csv, log_output_csv, model_file, encoder_file):
    print(f"Starting Complete DASP-DAFO Performance Evaluation...")
    
    # 1. Setup Keys
    if not os.path.exists("private.pem"):
        print("Error: Keys not found. Run step3_dasp_dafo_engine.py first.")
        return
    with open("private.pem", "rb") as f:
        private_key = SigningKey.from_pem(f.read())
    public_key = private_key.get_verifying_key()
    
    # Load ML Model
    model = xgb.XGBClassifier()
    model.load_model(model_file)
    label_encoder = joblib.load(encoder_file)
    
    # Load data
    df = pd.read_csv(input_csv)
    
    metrics_log = []
    previous_hash = "0" * 64
    total_buffer_bytes = 0
    
    print(f"Running benchmarks on {len(df)} records. This might take a few seconds...")
    
    for index, row in df.iterrows():
        metric = {
            "entry_id": int(row['entry_id']),
            "ml_inference_time_ms": 0.0,
            "hash_time_ms": 0.0,
            "ecdsa_sign_time_ms": 0.0,
            "ecdsa_verify_time_ms": 0.0,
            "packet_size_bytes": 0,
            "total_processing_latency_ms": 0.0
        }
        
        start_total = time.time()
        
        # --- 1. Measure ML Inference Time ---
        start_ml = time.time()
        features = pd.DataFrame([{
            'N': row['Nitrogen'], 
            'P': row['Phosphorus'], 
            'K': row['Potassium'], 
            'temperature': row['Temperature'], 
            'ph': row['pH']
        }])
        crop_encoded = model.predict(features)[0]
        predicted_crop = label_encoder.inverse_transform([crop_encoded])[0]
        predicted_irrigation = bool(row['Moisture'] < 50)
        metric['ml_inference_time_ms'] = (time.time() - start_ml) * 1000
        
        calculated_criticality = 0.9 if predicted_irrigation else 0.2
        
        # Build Base Packet
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
            "Predicted_Irrigation": predicted_irrigation,
            "Predicted_Crop": predicted_crop,
            "Criticality": calculated_criticality,
            "Priority": (0.5 * calculated_criticality) + (0.2 * row['Quality']),
            "previous_hash": previous_hash
        }
        
        packet_string = json.dumps(packet_data, sort_keys=True).encode('utf-8')
        
        # --- 2. Measure Hash Time ---
        start_hash = time.time()
        current_hash = hashlib.sha256(packet_string).hexdigest()
        metric['hash_time_ms'] = (time.time() - start_hash) * 1000
        
        # --- 3. Measure ECDSA Sign Time ---
        start_sign = time.time()
        signature = private_key.sign(packet_string).hex()
        metric['ecdsa_sign_time_ms'] = (time.time() - start_sign) * 1000
        
        final_packet = packet_data.copy()
        final_packet["hash"] = current_hash
        final_packet["signature"] = signature
        final_packet["sync_status"] = "pending"
        
        packet_bytes = len(json.dumps(final_packet).encode('utf-8'))
        metric['packet_size_bytes'] = packet_bytes
        total_buffer_bytes += packet_bytes
        
        # --- 4. Measure ECDSA Verify Time ---
        start_verify = time.time()
        try:
            is_valid = public_key.verify(bytes.fromhex(signature), packet_string)
        except Exception:
            pass
        metric['ecdsa_verify_time_ms'] = (time.time() - start_verify) * 1000
        
        metric['total_processing_latency_ms'] = (time.time() - start_total) * 1000
        
        metrics_log.append(metric)
        previous_hash = current_hash
        
    # Save Metrics to CSV
    metrics_df = pd.DataFrame(metrics_log)
    metrics_df.to_csv(log_output_csv, index=False)
    
    # Calculate Averages for the console
    print("\n================ EXPERIMENT RESULTS ================")
    print(f"Total Packets Evaluated:       {len(df)}")
    print(f"Average Packet Size:           {metrics_df['packet_size_bytes'].mean():.2f} bytes")
    print(f"Total Buffer Utilization:      {total_buffer_bytes / 1024:.2f} KB (SD Card storage)")
    print(f"----------------------------------------------------")
    print(f"Average ML Inference Time:     {metrics_df['ml_inference_time_ms'].mean():.4f} ms")
    print(f"Average SHA-256 Hash Time:     {metrics_df['hash_time_ms'].mean():.4f} ms")
    print(f"Average ECDSA Sign Time:       {metrics_df['ecdsa_sign_time_ms'].mean():.4f} ms")
    print(f"Average ECDSA Verify Time:     {metrics_df['ecdsa_verify_time_ms'].mean():.4f} ms")
    print(f"Avg Total Processing Latency:  {metrics_df['total_processing_latency_ms'].mean():.4f} ms")
    print("====================================================\n")
    
    print(f"✅ Detailed metrics saved to: {log_output_csv}")

if __name__ == "__main__":
    evaluate_metrics("enriched_sensor_data.csv", "DASP_DAFO_experiment_log.csv", "universal_crop_xgboost.json", "crop_label_encoder.pkl")
