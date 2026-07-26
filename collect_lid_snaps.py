import sounddevice as sd
import numpy as np
import os
import time

from utils import find_builtin_mic, SAMPLE_RATE

# 350ms Audio Window for Double-Tap / Click Impulse
DOUBLE_TAP_WINDOW = 16800  # 350ms at 48.0kHz
DATASET_DIR = "dataset_double_taps"
CATEGORY = "noise_and_typing"
TARGET_EXTRA_SAMPLES = 200

def main():
    target_dir = os.path.join(DATASET_DIR, CATEGORY)
    os.makedirs(target_dir, exist_ok=True)
    
    existing_files = [f for f in os.listdir(target_dir) if f.startswith("lid_snap_")]
    collected_count = len(existing_files)
    
    device_id, dev_name = find_builtin_mic()
    
    print("==========================================================================")
    print("      MORSE - Hard Negative Lid Snap & Click Dataset Collector           ")
    print("==========================================================================")
    print(f"🎙️ Target Hardware: [{device_id}] {dev_name}")
    print(f"📁 Target Folder  : dataset/noise_and_typing/")
    print("🎯 Goal: Collect 100 earphone lid snaps & air clicks into noise_and_typing!")
    print("\n👉 Instructions:")
    print("   Open and close your earphone lid (or click a pen / snap fingers).")
    print("   Each click will be automatically recorded as a hard negative sample!")
    print(f"   Progress: {collected_count}/{TARGET_EXTRA_SAMPLES}")
    print("Press Ctrl+C to stop anytime.\n")

    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)
    last_trigger_time = 0.0

    def callback(indata, frames, time_info, status):
        nonlocal collected_count, last_trigger_time, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()

        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig

        # Trigger on sound peak with 0.40s debounce (captures soft lid snaps down to 1.8 vol)
        if volume >= 1.8 and (current_time - last_trigger_time) > 0.40:
            last_trigger_time = current_time
            collected_count += 1
            
            file_path = os.path.join(target_dir, f"lid_snap_{int(time.time()*1000)}.npy")
            np.save(file_path, buffer_history.copy())
            
            print(f"✅ [{collected_count}/{TARGET_EXTRA_SAMPLES}] Captured Lid Snap! Vol: {volume:4.1f} -> {os.path.basename(file_path)}")
            
            if collected_count >= TARGET_EXTRA_SAMPLES:
                print("\n🎉 GOAL REACHED! Collected 100 Lid Snap samples!")
                os._exit(0)

    try:
        with sd.InputStream(device=device_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print(f"\n👋 Stopped collection. Total lid snaps saved: {collected_count}")

if __name__ == "__main__":
    main()
