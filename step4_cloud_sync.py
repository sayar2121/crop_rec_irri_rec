import json
import hashlib
from datetime import datetime
from ecdsa import VerifyingKey, SECP256k1

def cloud_verify_packet(packet, public_key, expected_previous_hash):
    """
    Simulates the Cloud layer verifying the cryptography.
    """
    packet_data = packet.copy()
    
    # Remove the fields that were added AFTER the hash was computed
    packet_hash = packet_data.pop("hash")
    packet_sig = packet_data.pop("signature")
    packet_data.pop("sync_status", None)
    packet_data.pop("FairnessScore", None)
    
    packet_string = json.dumps(packet_data, sort_keys=True).encode('utf-8')
    
    # 1. Verify Hash Chain (Tamper detection)
    recomputed_hash = hashlib.sha256(packet_string).hexdigest()
    if recomputed_hash != packet_hash:
        return False, "Hash mismatch - Data corrupted or tampered"
        
    if packet_data["previous_hash"] != expected_previous_hash:
        return False, f"Previous hash mismatch - Chain broken at Seq {packet_data['seq']}"
        
    # 2. Verify ECDSA Signature (Authentication)
    try:
        is_valid = public_key.verify(bytes.fromhex(packet_sig), packet_string)
        if not is_valid:
            return False, "Invalid ECDSA signature"
    except Exception as e:
        return False, f"Signature verification error: {e}"
        
    return True, "Valid"

def run_cloud_sync(buffer_file):
    print(f"Reading offline buffer from {buffer_file}...")
    
    # Load the public key that the Cloud has on file for this Dew Node
    try:
        with open("public.pem", "rb") as f:
            public_key = VerifyingKey.from_pem(f.read())
    except FileNotFoundError:
        print("Public key not found! Cannot verify.")
        return
        
    packets = []
    with open(buffer_file, 'r') as f:
        for line in f:
            packets.append(json.loads(line.strip()))
            
    if not packets:
        print("No pending packets to sync.")
        return
        
    # --- DASP-DAFO FAIR ORDERING ---
    lambda1, lambda2, lambda3, lambda4 = 0.4, 0.3, 0.2, 0.1
    # Simulating current time as a few hours after the first packet
    current_time_sim = datetime.strptime("2026-09-26 15:00:00 UTC", "%Y-%m-%d %H:%M:%S UTC")
    
    print("Applying DASP-DAFO Fair Ordering algorithm...")
    for p in packets:
        packet_time = datetime.strptime(p['timestamp'], "%Y-%m-%d %H:%M:%S UTC")
        age_seconds = max(0, (current_time_sim - packet_time).total_seconds())
        
        # Normalizing Age (e.g., max considered age is 3 hours)
        normalized_age = min(age_seconds / 10800.0, 1.0)
        
        # F_i = lambda1*P_i + lambda2*Age_i + lambda3*C_i + lambda4*Q_i
        fairness_score = (lambda1 * p['Priority']) + (lambda2 * normalized_age) + \
                         (lambda3 * p['Criticality']) + (lambda4 * p['Quality'])
                         
        p['FairnessScore'] = fairness_score
        
    # Sort packets for transmission based on FairnessScore (Highest first)
    transmission_queue = sorted(packets, key=lambda x: x['FairnessScore'], reverse=True)
    
    print(f"\nTransmission Queue Reordered!")
    print(f"Top packet in queue: Seq {transmission_queue[0]['seq']} (Highest Fairness: {transmission_queue[0]['FairnessScore']:.3f})")
    print(f"Last packet in queue: Seq {transmission_queue[-1]['seq']} (Lowest Fairness: {transmission_queue[-1]['FairnessScore']:.3f})\n")
    
    print("Initiating Transmission to Cloud...")
    print("Cloud receiving and verifying packets...")
    
    # --- CLOUD VERIFICATION ---
    # The Cloud must reassemble the packets by Sequence Number to verify the Hash Chain
    cloud_buffer = sorted(transmission_queue, key=lambda x: x['seq'])
    
    verified_count = 0
    failed_count = 0
    expected_hash = "0" * 64  # Initial genesis hash
    
    for p in cloud_buffer:
        is_valid, reason = cloud_verify_packet(p, public_key, expected_hash)
        if is_valid:
            verified_count += 1
            expected_hash = p['hash']
        else:
            print(f"❌ Packet Seq {p['seq']} failed verification: {reason}")
            failed_count += 1
            break
            
    print(f"\n--- SYNC COMPLETE ---")
    print(f"✅ Packets Verified & Stored on Cloud: {verified_count}")
    if failed_count > 0:
        print(f"❌ Packets Failed/Dropped: {failed_count}")
        
    if verified_count == len(packets):
        print("\nAll packets verified successfully! Cloud sending ACK to Dew Node.")
        print("Dew Node clearing local offline buffer (Simulated).")
        # In production: os.remove(buffer_file)
        
if __name__ == "__main__":
    run_cloud_sync("dew_local_buffer.jsonl")
