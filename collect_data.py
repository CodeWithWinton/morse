import sounddevice as sd
import numpy as np
import os
import time

SAMPLE_RATE = 44100
WINDOW_SIZE = 2048  # 46.4ms window captures full transient impact & decay
DATASET_DIR = "dataset"
CATEGORIES = ["tap", "typing", "desk_tap", "palm_rest", "noise"]

def record_sample(category_name):
    target_dir = os.path.join(DATASET_DIR, category_name)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"\n--- COLLECTING: {category_name.upper()} ---")
    print(f"Make the sound for '{category_name}' when volume spikes!")
    print("Press Ctrl+C to finish this category.\n")
    
    sample_count = len(os.listdir(target_dir))
    last_trigger_time = 0
    buffer_history = np.zeros(WINDOW_SIZE)
    
    def callback(indata, frames, time_info, status):
        nonlocal sample_count, last_trigger_time, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()
        
        # Maintain rolling buffer window
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        # Trigger on volume spike > 2.0 with 0.35s debounce
        if volume > 2.0 and (current_time - last_trigger_time > 0.35):
            last_trigger_time = current_time
            sample_count += 1
            filename = os.path.join(target_dir, f"sample_{sample_count:04d}.npy")
            np.save(filename, buffer_history.copy())
            print(f"✅ Saved 46.4ms sample #{sample_count:04d} -> {filename} (Vol: {volume:.1f})")

    # Explicitly find and select Built-in Microphone hardware device
    devices = sd.query_devices()
    builtin_device_id = None
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and ("built-in" in dev['name'].lower() or "macbook" in dev['name'].lower()):
            builtin_device_id = i
            break

    try:
        with sd.InputStream(device=builtin_device_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print(f"\nStopped collecting for '{category_name}'. Total saved: {sample_count}\n")

def main():
    os.makedirs(DATASET_DIR, exist_ok=True)
    while True:
        print("====================================")
        print("   MORSE - ML Dataset Collector     ")
        print("====================================")
        print("Select category to collect:")
        for idx, cat in enumerate(CATEGORIES, 1):
            print(f"{idx}. {cat.replace('_', ' ').title()}")
        print(f"{len(CATEGORIES)+1}. Exit")
        
        choice = input(f"\nEnter choice (1-{len(CATEGORIES)+1}): ").strip()
        if choice.isdigit():
            c_int = int(choice)
            if 1 <= c_int <= len(CATEGORIES):
                record_sample(CATEGORIES[c_int - 1])
            elif c_int == len(CATEGORIES) + 1:
                print("Goodbye!")
                break
            else:
                print("Invalid choice, try again.\n")
        else:
            print("Invalid input.\n")

if __name__ == "__main__":
    main()
