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
    print("Press Ctrl+C anytime to finish this category.\n")
    
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
            print(f"   ✅ Saved [{collected_this_session}/{target_count}]: {filename} (Vol: {volume:.1f})")

    try:
        with sd.InputStream(device=device_id, channels=1, samplerate=SAMPLE_RATE, callback=callback):
            while collected_this_session < target_count:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n⏹️  Stopped '{category_name}'. Collected {collected_this_session} samples.")
        
    return collected_this_session

def main():
    print("==========================================================================")
    print("      MORSE - Daily Continuous Active Learning (CAL) Collector            ")
    print("==========================================================================")
    print("📅 Daily Goal: +200 Left Palm Taps | +200 Right Palm Taps | +300 Noise & Snaps")
    
    c1 = collect_category("double_left_palm", 200, "Double-tap the LEFT metal palm rest")
    c2 = collect_category("double_right_palm", 200, "Double-tap the RIGHT metal palm rest")
    c3 = collect_category("noise_and_typing", 300, "Make ambient noise, type, snap lid, & click pens")
    
    print("\n==========================================================================")
    print(f"🎉 Daily Collection Complete! Total new samples captured: {c1 + c2 + c3}")
    print("Run 'python3 train_double_tap_model.py' now to retrain TLM 1.0!")
    print("==========================================================================")

if __name__ == "__main__":
    main()
