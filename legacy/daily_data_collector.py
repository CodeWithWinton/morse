import sounddevice as sd
import numpy as np
import time
import os
import sys

from utils import find_builtin_mic, SAMPLE_RATE

DOUBLE_TAP_WINDOW = 24000  # 500ms window at 48.0kHz
DATASET_DIR = "dataset_double_taps"

def calibrate_ambient_noise(device_id, duration_sec=1.0):
    """Measure local ambient room noise floor to set laptop-specific trigger thresholds."""
    print("⏳ Auto-calibrating laptop mic noise floor (keep room quiet for 1 sec)...")
    vols = []
    peaks = []
    
    def calib_cb(indata, frames, time_info, status):
        sig = indata.flatten()
        vols.append(np.linalg.norm(sig) * 10)
        peaks.append(np.max(np.abs(sig)))
        
    with sd.InputStream(device=device_id, channels=1, samplerate=SAMPLE_RATE, callback=calib_cb):
        time.sleep(duration_sec)
        
    amb_vol = float(np.median(vols)) if vols else 5.0
    amb_peak = float(np.median(peaks)) if peaks else 0.01
    
    # Set dynamic trigger thresholds relative to local mic sensitivity
    target_vol = max(25.0, amb_vol * 2.5)
    target_peak = max(0.06, amb_peak * 3.0)
    print(f"✅ Mic Calibrated! Ambient Vol: {amb_vol:.1f} | Trigger Floor -> Vol > {target_vol:.1f}, Peak > {target_peak:.3f}\n")
    return target_vol, target_peak

def collect_category(category_name, target_count, prompt_msg):
    target_dir = os.path.join(DATASET_DIR, category_name)
    os.makedirs(target_dir, exist_ok=True)
    
    existing_files = [f for f in os.listdir(target_dir) if f.endswith(".npy")]
    initial_count = len(existing_files)
    collected_this_session = 0
    
    device_id, dev_name = find_builtin_mic()
    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)
    last_trigger_time = 0.0

    # Auto-Calibrate Noise Floor for local laptop hardware (MacBook Air vs Neo vs Pro)
    if category_name == "noise_and_typing":
        min_volume_threshold = 3.0
        min_peak_threshold = 0.01
    else:
        min_volume_threshold, min_peak_threshold = calibrate_ambient_noise(device_id, duration_sec=1.0)
    
    print("==========================================================================")
    print(f" 👉 RECORDING CATEGORY: {category_name.upper()}")
    print("==========================================================================")
    print(f"   Prompt: {prompt_msg}")
    if category_name == "noise_and_typing":
        print("   Trigger Mode: Ambient / Typing Auto-Stream (Vol >= 3.0)")
    else:
        print(f"   Trigger Mode: Kinetic Impact Spike (Peak >= {min_peak_threshold:.3f} & Vol >= {min_volume_threshold:.1f})")
    print(f"   Target for this session: {target_count} samples")
    print(f"   Existing samples in folder: {initial_count}")
    print("   Press Ctrl+C anytime to stop and return to main menu.\n")
    
    def callback(indata, frames, time_info, status):
        nonlocal collected_this_session, last_trigger_time, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        peak_amp = np.max(np.abs(sig))
        current_time = time.time()
        
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        # Laptop-Specific Auto-Calibrated Trigger Condition
        valid_trigger = False
        if category_name == "noise_and_typing":
            valid_trigger = (volume >= 3.0)
        else:
            valid_trigger = (peak_amp >= min_peak_threshold) and (volume >= min_volume_threshold)

        # 0.50s lockout window to capture full 500ms tap window
        if valid_trigger and (current_time - last_trigger_time > 0.50):
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
            print(f"   ⚡ [{collected_this_session}/{target_count}] Total: {total_now} | Saved sample (Peak: {peak_amp:.3f}, Vol: {volume:.1f})")

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
