import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings('ignore')

def preprocess_universal_data(input_file, output_file):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # 1. Rename columns to match what our Dew node expects.
    # We will use 'humidity' as a proxy for 'Moisture' for the irrigation logic
    rename_map = {
        'N': 'Nitrogen',
        'P': 'Phosphorus',
        'K': 'Potassium',
        'temperature': 'Temperature',
        'humidity': 'Moisture',
        'ph': 'pH',
        'label': 'Recommended_Crop'
    }
    df = df.rename(columns=rename_map)
    
    # 2. Add 'entry_id' and 'created_at' to simulate a real-time IoT sensor stream
    df['entry_id'] = range(1, len(df) + 1)
    
    # Generate mock timestamps, e.g., 10 minutes apart
    start_time = datetime(2026, 9, 26, 12, 0, 0)
    df['created_at'] = [(start_time + timedelta(minutes=10*i)).strftime('%Y-%m-%d %H:%M:%S UTC') for i in range(len(df))]
    
    # 3. Simulate Data Quality (Q)
    # To test DASP-DAFO correctly, we need some low-quality packets.
    # Let's say randomly 5% of the data has poor quality (Q=0.5).
    np.random.seed(42)
    df['Quality'] = np.random.choice([1.0, 0.5], size=len(df), p=[0.95, 0.05])
    
    # 4. Calculate Irrigation Ground Truth and Criticality (C)
    # The 'Moisture' (humidity from Kaggle) ranges from ~14 to ~100.
    # If Moisture is < 50, let's say it needs irrigation (High Criticality).
    df['Irrigation_Required'] = df['Moisture'] < 50
    df['Criticality'] = df['Irrigation_Required'].apply(lambda req: 0.9 if req else 0.2)
    
    # Save the processed dataset
    df.to_csv(output_file, index=False)
    print(f"\nSuccessfully generated enriched simulation data: {output_file}")
    print(f"Total records processed: {len(df)}")
    
    # Display a preview of the important columns
    preview_cols = ['entry_id', 'created_at', 'Moisture', 'Irrigation_Required', 'Criticality', 'Quality', 'Recommended_Crop']
    print("\n--- Preview of Enriched Data (First 5 rows) ---")
    print(df[preview_cols].head())

if __name__ == "__main__":
    input_csv = "Crop_recommendation.csv"
    output_csv = "enriched_sensor_data.csv"
    preprocess_universal_data(input_csv, output_csv)
