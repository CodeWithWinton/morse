import sounddevice as sd
import numpy as np
import time
import os
import sys

from utils import find_builtin_mic, SAMPLE_RATE, compute_vibration_trail_ratio

DOUBLE_TAP_WINDOW = 16800  # 350ms at 48.0kHz
DATASET_DIR = "dataset_double_taps"

def main():
    print("==========================================================================")
    print("  MORSE — Auto-Stream Continuous Dataset Collector (Target: 1 Lakh)")
    print("==========================================================================")
    print("🎧 Continuous Background Recording Active...")
    print("💡 Tap left or right palm rest while working. Auto-labeled & saved continuously!")
    print("Press Ctrl+C to stop stream session.\n")
    
    device_id, dev_name = find_builtin_mic()
    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)
    last_trigger_time = 0.0
    saved_count = 0
    
    left_dir = os.path.join(DATASET_DIR, "double_left_palm")
    right_dir = os.path.join(DATASET_DIR, "double_right_palm")
    noise_dir = os.path.join(DATASET_DIR, "noise_and_typing")
    
    for d in [left_dir, right_dir, noise_dir]:
        os.makedirs(d, exist_ok=True)
        
    def callback(indata, frames, time_info, status):
        nonlocal saved_count, last_trigger_time, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()
        
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        if volume >= 2.0 and (current_time - last_trigger_time) > 0.35:
            last_trigger_time = current_time
            dispersion = compute_vibration_trail_ratio(buffer_history)
            
            # Physics Quality Guardian Filter
            if dispersion < 0.14:
                category = "noise_and_typing"
                target_path = os.path.join(noise_dir, f"noise_{int(current_time * 1000)}.npy")
            else:
                # Spatial Frequency Proximity Check
                fft_full = np.abs(np.fft.rfft(buffer_history))
                total_e = np.sum(fft_full) + 1e-6
                freqs = np.fft.rfftfreq(len(buffer_history), d=1.0/SAMPLE_RATE)
                bass_ratio = np.sum(fft_full[(freqs >= 120) & (freqs <= 600)]) / total_e
                
                if bass_ratio >= 0.48:
                    category = "double_left_palm"
                    target_path = os.path.join(left_dir, f"left_{int(current_time * 1000)}.npy")
                else:
                    category = "double_right_palm"
                    target_path = os.path.join(right_dir, f"right_{int(current_time * 1000)}.npy")
                    
            np.save(target_path, buffer_history)
            saved_count += 1
            print(f"   ⚡ Auto-Captured [{saved_count}]: {category} (Vol: {volume:.1f}, Disp: {dispersion:.2f})")

    try:
        with sd.InputStream(device=device_id, channels=1, samplerate=SAMPLE_RATE, callback=callback):
            while True:
                time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"\n⏹️ Stream session ended cleanly. Captured {saved_count} high-quality samples!")

if __name__ == "__main__":
    main()
