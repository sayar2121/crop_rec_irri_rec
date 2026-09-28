import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def generate_graphs(log_file):
    print(f"Loading data from {log_file}...")
    df = pd.read_csv(log_file)
    
    # Apply global plotting styles for academic look
    plt.style.use('seaborn-v0_8-darkgrid')
    sns.set_context("paper", font_scale=1.5)
    
    print("Generating Latency Breakdown Bar Chart...")
    # --- 1. Latency Breakdown Bar Chart ---
    labels = ['ML Inference', 'SHA-256 Hash', 'ECDSA Signing']
    avg_times = [
        df['ml_inference_time_ms'].mean(),
        df['hash_time_ms'].mean(),
        df['ecdsa_sign_time_ms'].mean()
    ]
    
    plt.figure(figsize=(8, 6))
    bars = sns.barplot(x=labels, y=avg_times, palette=['#3498db', '#e74c3c', '#2ecc71'])
    plt.title('DASP-DAFO Node Processing Latency Breakdown', fontsize=16)
    plt.ylabel('Average Time (Milliseconds)', fontsize=14)
    
    # Add exact values on top of bars
    for bar in bars.patches:
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
                 f"{bar.get_height():.3f} ms", ha='center', fontsize=12)
                 
    plt.tight_layout()
    plt.savefig('latency_breakdown.png', dpi=300)
    plt.close()
    
    print("Generating Latency Stability Line Graph...")
    # --- 2. Total Latency Stability over 2200 packets ---
    plt.figure(figsize=(10, 6))
    plt.plot(df['entry_id'], df['total_processing_latency_ms'], color='#9b59b6', linewidth=1, alpha=0.7)
    plt.title('DASP-DAFO Edge Processing Stability', fontsize=16)
    plt.xlabel('Packet Sequence Number', fontsize=14)
    plt.ylabel('Total Latency (ms)', fontsize=14)
    
    # Add a trendline to prove stability over time
    z = np.polyfit(df['entry_id'], df['total_processing_latency_ms'], 1)
    p = np.poly1d(z)
    plt.plot(df['entry_id'], p(df['entry_id']), "k--", linewidth=2, label="Trendline")
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('latency_stability.png', dpi=300)
    plt.close()
    
    print("Generating Buffer Growth Graph...")
    # --- 3. Buffer Growth (Cumulative Size) ---
    df['cumulative_size_kb'] = df['packet_size_bytes'].cumsum() / 1024
    
    plt.figure(figsize=(10, 6))
    plt.plot(df['entry_id'], df['cumulative_size_kb'], color='#f39c12', linewidth=2)
    plt.fill_between(df['entry_id'], df['cumulative_size_kb'], color='#f39c12', alpha=0.3)
    plt.title('Offline Buffer Utilization over Time', fontsize=16)
    plt.xlabel('Number of Packets Stored Offline', fontsize=14)
    plt.ylabel('Buffer Size (Kilobytes)', fontsize=14)
    
    plt.tight_layout()
    plt.savefig('buffer_growth.png', dpi=300)
    plt.close()

    print("\n✅ All graphs successfully generated for your research paper!")
    print("Saved as:")
    print(" 1. latency_breakdown.png")
    print(" 2. latency_stability.png")
    print(" 3. buffer_growth.png")

if __name__ == "__main__":
    generate_graphs("DASP_DAFO_experiment_log.csv")
