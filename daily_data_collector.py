import sounddevice as sd
import numpy as np
import time
import os
import sys

from utils import find_builtin_mic, SAMPLE_RATE

DOUBLE_TAP_WINDOW = 24000  # 500ms window at 48.0kHz
DATASET_DIR = "dataset_double_taps"

def collect_category(category_name, target_count, prompt_msg):
    target_dir = os.path.join(DATASET_DIR, category_name)
    os.makedirs(target_dir, exist_ok=True)
    
    existing_files = [f for f in os.listdir(target_dir) if f.endswith(".npy")]
    initial_count = len(existing_files)
    collected_this_session = 0
    
    device_id, dev_name = find_builtin_mic()
    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)
    last_trigger_time = 0.0

    # Physical Tap Volume & Transient Guards:
    # Ambient room noise (Vol 4-5, Crest <2.0) is blocked.
    # Soft taps (Vol 8-11, Crest >3.0) and Hard taps are captured cleanly.
    min_volume_threshold = 3.0 if category_name == "noise_and_typing" else 7.5
    
    print("\n==========================================================================")
    print(f" 👉 RECORDING CATEGORY: {category_name.upper()}")
    print("==========================================================================")
    print(f"   Prompt: {prompt_msg}")
    print(f"   Required Trigger Volume: > {min_volume_threshold}")
    print(f"   Target for this session: {target_count} samples")
    print(f"   Existing samples in folder: {initial_count}")
    print("   Press Ctrl+C anytime to stop and return to main menu.\n")
    
    def callback(indata, frames, time_info, status):
        nonlocal collected_this_session, last_trigger_time, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()
        
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        # Crest factor check to reject continuous ambient background noise
        rms = np.sqrt(np.mean(buffer_history ** 2)) + 1e-6
        crest_factor = np.max(np.abs(buffer_history)) / rms
        
        valid_trigger = False
        if category_name == "noise_and_typing":
            valid_trigger = (volume >= min_volume_threshold)
        else:
            valid_trigger = (volume >= min_volume_threshold) and (crest_factor >= 2.5)

        # Lockout window of 0.50s to capture full 500ms tap window
        if valid_trigger and (current_time - last_trigger_time) > 0.50:
            last_trigger_time = current_time
            collected_this_session += 1
            filename = f"{category_name}_{int(current_time * 1000)}.npy"
            filepath = os.path.join(target_dir, filename)
            
            # 1. Save .npy file
            np.save(filepath, buffer_history)
            
            # 2. Dual-Save: Append directly to morse_dataset.h5 (float32)
            try:
                from convert_dataset import append_sample_to_h5
                append_sample_to_h5(category_name, buffer_history)
            except Exception:
                pass

            # Print live counter feedback on EVERY SINGLE TAP!
            total_now = initial_count + collected_this_session
            print(f"   ⚡ [{collected_this_session}/{target_count}] Total: {total_now} | Saved sample (Vol: {volume:.1f})")

    try:
        with sd.InputStream(device=device_id, channels=1, samplerate=SAMPLE_RATE, callback=callback):
            while collected_this_session < target_count:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Session paused for '{category_name}'. Collected {collected_this_session} new samples.")
        
    return collected_this_session

def main():
    while True:
        print("\n==========================================================================")
        print("     MORSE — TLM 1.5 DATASET SPRINT COLLECTOR (INTERACTIVE MENU)          ")
        print("==========================================================================")
        print("Select category to collect:")
        print("  1. Double-Tap LEFT Palm Rest (Target: 6,000 samples)")
        print("  2. Double-Tap RIGHT Palm Rest (Target: 6,000 samples)")
        print("  3. Ambient Noise, Typing, Lid Snaps & TV Audio (Target: 8,000 samples)")
        print("  4. Exit Collector")
        
        choice = input("\nEnter choice (1, 2, 3, or 4): ").strip()
        
        if choice == "1":
            collect_category("double_left_palm", 6000, "Double-tap the LEFT metal palm rest (Soft, Med, Hard)")
        elif choice == "2":
            collect_category("double_right_palm", 6000, "Double-tap the RIGHT metal palm rest (Soft, Med, Hard)")
        elif choice == "3":
            collect_category("noise_and_typing", 8000, "Make ambient noise, type, snap lid, click pens, & play TV/music")
        elif choice == "4":
            print("👋 Exiting Data Collector.")
            break
        else:
            print("❌ Invalid choice! Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
