import sounddevice as sd
import numpy as np
import os
import time

from utils import find_builtin_mic, SAMPLE_RATE

# 500ms Audio Window for Full Double-Tap Gesture
DOUBLE_TAP_WINDOW = 24000  # 500ms at 48.0kHz
DATASET_DIR = "dataset_double_taps"
CATEGORIES = ["double_left_palm", "double_right_palm", "noise_and_typing"]
TARGET_SAMPLES = 800

def record_category(category_name):
    target_dir = os.path.join(DATASET_DIR, category_name)
    os.makedirs(target_dir, exist_ok=True)
    
    existing_files = [f for f in os.listdir(target_dir) if f.endswith(".npy")]
    sample_count = len(existing_files)
    
    print(f"\n============================================================")
    print(f" 🎙️ COLLECTING: {category_name.upper()}")
    print(f"============================================================")
    if category_name == "double_left_palm":
        print("👉 Perform DOUBLE-TAPS on the LEFT metal palm rest.")
    elif category_name == "double_right_palm":
        print("👉 Perform DOUBLE-TAPS on the RIGHT metal palm rest.")
    else:
        print("👉 Perform TYPING, DESK BUMPSI, WRIST SLIDES, or AMBIENT NOISE.")
        
    print(f"Goal: {TARGET_SAMPLES} samples. Current: {sample_count}/{TARGET_SAMPLES}")
    print("Press Ctrl+C to stop collecting for this category.\n")
    
    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)
    last_trigger_time = 0.0
    
    # Volume trigger threshold
    min_vol = 1.5 if category_name == "double_right_palm" else 2.5

    def callback(indata, frames, time_info, status):
        nonlocal sample_count, last_trigger_time, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()
        
        # Maintain rolling 500ms buffer
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        # Trigger on initial impact spike with a 0.60s debounce for full 500ms capture
        if volume >= min_vol and (current_time - last_trigger_time > 0.60):
            last_trigger_time = current_time
            sample_count += 1
            filename = os.path.join(target_dir, f"sample_{sample_count:04d}.npy")
            np.save(filename, buffer_history.copy())
            print(f" ✅ [{sample_count:03d}/{TARGET_SAMPLES}] Saved 500ms gesture -> {filename} (Vol: {volume:.1f})")
            
            if sample_count >= TARGET_SAMPLES:
                print(f"\n🎉 Reached target of {TARGET_SAMPLES} samples for '{category_name}'!")

    builtin_device_id, dev_name = find_builtin_mic()
    print(f"🎙️ Target Hardware: [{builtin_device_id}] {dev_name}")

    try:
        with sd.InputStream(device=builtin_device_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while sample_count < TARGET_SAMPLES:
                sd.sleep(500)
    except KeyboardInterrupt:
        print(f"\nStopped collecting for '{category_name}'. Saved: {sample_count}/{TARGET_SAMPLES}\n")

def main():
    os.makedirs(DATASET_DIR, exist_ok=True)
    while True:
        print("\n==============================================")
        print("   MORSE - 500ms Double-Tap Dataset Collector  ")
        print("==============================================")
        for idx, cat in enumerate(CATEGORIES, 1):
            target_dir = os.path.join(DATASET_DIR, cat)
            count = len([f for f in os.listdir(target_dir) if f.endswith(".npy")]) if os.path.exists(target_dir) else 0
            print(f"{idx}. {cat.replace('_', ' ').title():25s} [{count}/{TARGET_SAMPLES} samples]")
        print(f"{len(CATEGORIES)+1}. Exit")
        
        choice = input(f"\nEnter choice (1-{len(CATEGORIES)+1}): ").strip()
        if choice.isdigit():
            c_int = int(choice)
            if 1 <= c_int <= len(CATEGORIES):
                record_category(CATEGORIES[c_int - 1])
            elif c_int == len(CATEGORIES) + 1:
                print("Goodbye!")
                break
            else:
                print("Invalid choice, try again.")
        else:
            print("Invalid input.")

if __name__ == "__main__":
    main()
