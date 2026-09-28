# DASP-DAFO IoT Agriculture Architecture

This repository contains the software implementation of the **DASP-DAFO** (Dew Assisted Sensor Protocol with Data Anomaly Fair Ordering) architecture for Smart Agriculture. 

Designed for Edge/Dew computing environments (like ESP8266 nodes and offline smartphones), this system integrates **Machine Learning (XGBoost)** for crop and irrigation recommendations with **Blockchain-grade Cryptography (SHA-256 & ECDSA)** for secure, offline-capable data buffering and cloud synchronization.

## 🏗 System Architecture

The architecture consists of two primary layers:

### 1. The Dew Layer (Edge Node / Mobile Cache)
- **Local AI Inference:** Utilizes a highly optimized XGBoost Machine Learning classifier to predict crop recommendations in under 1 millisecond using local sensor data (N, P, K, Temp, pH). Irrigation is determined via a deterministic threshold.
- **Data Security:** Secures every sensor reading using a continuous **SHA-256 Hash Chain** (tamper detection) and an **ECDSA secp256k1 Digital Signature** (authentication), forming a localized blockchain.
- **Priority Calculation:** Assigns a Priority Score to each reading based on packet *Criticality* (e.g., urgent irrigation needs) and *Quality*. It buffers this data offline in a local JSONL cache during network outages.

### 2. The Cloud Layer (Verification & Storage)
- **Fairness Synchronization:** Re-orders the buffered packets upon network reconnection using the DASP-DAFO mathematical fairness algorithm (weighing Priority, Age, Criticality, and Quality) to prevent packet starvation for older or low-priority packets.
- **Cryptographic Verification:** Re-hashes the chain and verifies all ECDSA signatures before successfully accepting the data into the cloud.

---

## 🚀 Getting Started

### Prerequisites
Ensure you have Python 3 installed. It is highly recommended to use a virtual environment.

```bash
python3 -m venv venv
source venv/bin/activate
```

### Installation
Install all required project dependencies:
```bash
pip install -r requirements.txt
pip install matplotlib seaborn
```

---

## 🛠 Running the Pipeline

The project is broken down into modular steps simulating the entire research architecture pipeline:

### 1. Data Preprocessing
Format the raw Kaggle dataset and simulate the IoT data stream with entry IDs, timestamps, and Quality metrics.
```bash
python3 step1_preprocess.py
```

### 2. Train the XGBoost AI Model
Train the Machine Learning classifier on the 22-crop universal dataset. This generates the lightweight `universal_crop_xgboost.json` model ready for edge deployment.
```bash
python3 step2_train_models.py
```

### 3. Run the DASP-DAFO Edge Engine
Simulates the offline Dew Node. It reads the sensor stream, makes real-time ML predictions, generates the SHA-256 hash chain, signs the data with ECDSA, and safely stores the secure packets in `dew_local_buffer.jsonl`.
```bash
python3 step3_dasp_dafo_engine.py
```

### 4. Cloud Synchronization & Verification
Simulates the internet reconnection. It applies the Fair Ordering algorithm to the offline queue and sends it to the Cloud, which mathematically verifies the cryptographic chain.
```bash
python3 step4_cloud_sync.py
```

---

## 📊 Evaluation & Research Metrics

To extract the exact millisecond latencies and storage metrics for academic research papers, run the evaluation script:

```bash
python3 step5_evaluate_metrics.py
```
This generates `DASP_DAFO_experiment_log.csv` containing detailed timings for ML inference, hashing, and ECDSA signing per packet.

To automatically visualize these results into publication-ready PNG graphs (Latency Breakdown, Stability, Buffer Utilization):
```bash
python3 step6_plot_graphs.py
```

---

## 💻 Interactive AI Predictor
You can manually test the XGBoost model by entering your own custom soil parameters (N, P, K, Temperature, pH, Moisture) via the command-line interface to get an instant crop recommendation:

```bash
python3 interactive_predictor.py
```
