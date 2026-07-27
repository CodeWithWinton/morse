import sounddevice as sd
import numpy as np
import time
import os
import sys

from utils import find_builtin_mic, SAMPLE_RATE

DOUBLE_TAP_WINDOW = 16800  # 350ms at 48.0kHz
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
    
    print(f"\n👉 {prompt_msg}")
    print(f"   Target for this session: {target_count} samples")
    print(f"   Existing files in '{category_name}': {initial_count}")
    print("Press Ctrl+C anytime to pause this category session.\n")
    
    def callback(indata, frames, time_info, status):
        nonlocal collected_this_session, last_trigger_time, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()
        
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        if volume >= 2.0 and (current_time - last_trigger_time) > 0.35:
            last_trigger_time = current_time
            collected_this_session += 1
            filename = f"{category_name}_{int(current_time * 1000)}.npy"
            filepath = os.path.join(target_dir, filename)
            np.save(filepath, buffer_history)
            if collected_this_session % 50 == 0 or collected_this_session == target_count:
                print(f"   ⚡ Progress [{collected_this_session}/{target_count}]: Saved {filename} (Vol: {volume:.1f})")

    try:
        with sd.InputStream(device=device_id, channels=1, samplerate=SAMPLE_RATE, callback=callback):
            while collected_this_session < target_count:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n⏹️ Session paused for '{category_name}'. Collected {collected_this_session} samples this run.")
        
    return collected_this_session

def main():
    print("==========================================================================")
    print("     MORSE — 4-DAY 1-LAKH INTENSIVE SPRINT COLLECTOR (30k/DAY)            ")
    print("==========================================================================")
    print("📅 Daily Sprint Goal: 9,000 Left | 9,000 Right | 12,000 Noise (Total: 30k/day)")
    
    c1 = collect_category("double_left_palm", 9000, "Double-tap the LEFT metal palm rest")
    c2 = collect_category("double_right_palm", 9000, "Double-tap the RIGHT metal palm rest")
    c3 = collect_category("noise_and_typing", 12000, "Make ambient noise, type, snap lid, & click pens")
    
    print("\n==========================================================================")
    print(f"🎉 Sprint Session Complete! Total new ground-truth samples: {c1 + c2 + c3}")
    print("Run 'python3 train_double_tap_model.py' to train on your updated dataset!")
    print("==========================================================================")

if __name__ == "__main__":
    main()
