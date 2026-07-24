import sounddevice as sd
import numpy as np
import os
import time

SAMPLE_RATE = 44100
DURATION = 0.25  # Record 250ms per sample
DATASET_DIR = "dataset"

def record_sample(category_name):
    target_dir = os.path.join(DATASET_DIR, category_name)
    os.makedirs(target_dir, exist_ok=True)
    
    print(f"\n--- COLLECTING: {category_name.upper()} ---")
    print(f"Make the sound for '{category_name}' when volume spikes!")
    print("Press Ctrl+C to finish this category.\n")
    
    sample_count = len(os.listdir(target_dir))
    last_trigger_time = 0
    
    def callback(indata, frames, time_info, status):
        nonlocal sample_count, last_trigger_time
        volume = np.linalg.norm(indata) * 10
        current_time = time.time()
        
        # Trigger on volume spike with 0.4s debounce
        if volume > 4.5 and (current_time - last_trigger_time > 0.4):
            last_trigger_time = current_time
            sample_count += 1
            filename = os.path.join(target_dir, f"sample_{sample_count:04d}.npy")
            np.save(filename, indata.copy())
            print(f"✅ Saved sample #{sample_count} -> {filename} (Vol: {volume:.1f})")

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
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
        print("1. Tap (Chassis taps)")
        print("2. Typing (Keyboard keypresses)")
        print("3. Noise (Aarti bell, background, speech)")
        print("4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        if choice == "1":
            record_sample("tap")
        elif choice == "2":
            record_sample("typing")
        elif choice == "3":
            record_sample("noise")
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice, try again.\n")

if __name__ == "__main__":
    main()
