"""
MORSE TLM 1.5 — Universal Cross-Platform Data Collector
======================================================
Works on macOS, Windows, and Linux.
Captures 500ms (24,000 samples @ 48.0kHz) physical tap and noise samples.
Auto-downmixes multi-channel audio to mono and calibrates local noise floor.
Features Smooth Peak Attack Triggering for 100% consistent tap collection.
"""

import os
import sys
import time
import platform
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    import sounddevice as sd
except ImportError:
    print("❌ sounddevice library not found. Installing dependencies...")
    os.system(f"{sys.executable} -m pip install sounddevice numpy scipy")
    import sounddevice as sd

SAMPLE_RATE = 48000
DOUBLE_TAP_WINDOW = 24000  # 500ms at 48.0kHz
DEFAULT_DATASET_DIR = "dataset_double_taps"
CATEGORIES = ["double_left_palm", "double_right_palm", "noise_and_typing"]


def get_default_input_device():
    """Finds system default audio input device across Windows, macOS, and Linux."""
    try:
        devices = sd.query_devices()
        default_in = sd.default.device[0]
        if default_in is not None and default_in >= 0:
            dev_info = devices[default_in]
            return dev_info.get('index', default_in), dev_info['name']
    except Exception:
        pass
    return None, "Default Input Microphone"


def auto_calibrate_noise_floor(device_id, duration_sec=1.0):
    """Measures local mic noise floor to set dynamic trigger thresholds for the local laptop."""
    print("⏳ Calibrating local microphone noise floor (keep room quiet for 1s)...")
    volumes = []
    peaks = []

    def calib_callback(indata, frames, time_info, status):
        sig = np.mean(indata, axis=1) if indata.ndim > 1 else indata.flatten()
        volumes.append(np.linalg.norm(sig) * 10)
        peaks.append(np.max(np.abs(sig)))

    try:
        with sd.InputStream(device=device_id, samplerate=SAMPLE_RATE, callback=calib_callback):
            time.sleep(duration_sec)
    except Exception:
        with sd.InputStream(samplerate=SAMPLE_RATE, callback=calib_callback):
            time.sleep(duration_sec)

    amb_vol = float(np.median(volumes)) if volumes else 3.0
    amb_peak = float(np.median(peaks)) if peaks else 0.008

    target_vol = max(12.0, amb_vol * 1.8)
    target_peak = max(0.04, amb_peak * 2.2)

    print(f"✅ Calibrated! Ambient Vol: {amb_vol:.1f} | Trigger Floor -> Vol > {target_vol:.1f}, Peak > {target_peak:.3f}\n")
    return target_vol, target_peak


def record_category(category_name, output_dir=DEFAULT_DATASET_DIR, target_count=100):
    """Interactive loop to collect tap or noise samples for a given category."""
    cat_dir = os.path.join(output_dir, category_name)
    os.makedirs(cat_dir, exist_ok=True)

    existing_files = [f for f in os.listdir(cat_dir) if f.endswith(".npy")]
    sample_count = len(existing_files)
    session_files = []
    stop_recording = False

    os_name = platform.system()
    dev_id, dev_name = get_default_input_device()

    print("==========================================================================")
    print(f" 🎙️ UNIVERSAL COLLECTOR [{os_name.upper()}] — {category_name.upper()}")
    print("==========================================================================")
    print(f" 💻 Hardware: [{dev_id}] {dev_name}")
    print(f" 📂 Destination: {os.path.abspath(cat_dir)}")
    print(f" 📊 Existing: {sample_count} samples | Goal: +{target_count} new samples in this session")

    if category_name == "double_left_palm":
        print(" 👉 Action: Perform DOUBLE-TAPS on the LEFT metal palm rest.")
    elif category_name == "double_right_palm":
        print(" 👉 Action: Perform DOUBLE-TAPS on the RIGHT metal palm rest.")
    else:
        print(" 👉 Action: Perform TYPING, DESK BUMPS, WRIST SLIDES, or AMBIENT NOISE.")

    print(" ⏹️ Press Ctrl+C to stop early and choose whether to keep session samples.\n")

    if category_name == "noise_and_typing":
        vol_floor = 4.0
        peak_floor = 0.015
    else:
        vol_floor, peak_floor = auto_calibrate_noise_floor(dev_id, duration_sec=1.0)

    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)
    last_trigger_time = 0.0

    def stream_callback(indata, frames, time_info, status):
        nonlocal sample_count, last_trigger_time, buffer_history, session_files, stop_recording

        if stop_recording:
            return

        # Downmix multi-channel stereo to 1D mono safely across all hardware
        if indata.ndim > 1 and indata.shape[1] > 1:
            sig = np.mean(indata, axis=1)
        else:
            sig = indata.flatten()

        volume = np.linalg.norm(sig) * 10
        peak = np.max(np.abs(sig))
        current_time = time.time()

        # Maintain 500ms rolling window (24,000 samples)
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig

        # Compute Crest Factor to reject low-energy continuous hums
        rms = np.sqrt(np.mean(buffer_history**2)) + 1e-6
        crest_factor = np.max(np.abs(buffer_history)) / rms

        is_tap_cat = category_name in ("double_left_palm", "double_right_palm")
        valid_impulse = (crest_factor >= 2.5) if is_tap_cat else True

        # Trigger logic with snappy 0.40s debounce window
        if volume >= vol_floor and peak >= peak_floor and valid_impulse and (current_time - last_trigger_time > 0.40):
            last_trigger_time = current_time
            sample_count += 1
            filename = os.path.join(cat_dir, f"sample_{sample_count:05d}.npy")
            np.save(filename, buffer_history.copy())
            session_files.append(filename)

            session_captured = len(session_files)
            print(f"  ✅ [{session_captured:03d}/{target_count}] Captured -> {os.path.basename(filename)} (Vol: {volume:.1f}, Peak: {peak:.3f}, Crest: {crest_factor:.1f})")

            # Check target session count cutoff!
            if session_captured >= target_count:
                print(f"\n🎉 Target goal of +{target_count} new samples reached!")
                stop_recording = True

    try:
        with sd.InputStream(device=dev_id, samplerate=SAMPLE_RATE, callback=stream_callback):
            while not stop_recording:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print(f"\n\n⏹️ Session stopped manually via Ctrl+C.")

    print(f"📊 Session Summary: Captured {len(session_files)} new samples.")
    if session_files:
        ans = input("❓ Keep these new session samples? (Y/n): ").strip().lower()
        if ans == "n":
            for fpath in session_files:
                if os.path.exists(fpath):
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass
            print(f"🗑️ Discarded {len(session_files)} session samples!")
        else:
            print(f"💾 Kept {len(session_files)} new session samples!")
    print()


def run_interactive_collector(output_dir=DEFAULT_DATASET_DIR):
    """Main CLI menu for universal data collection & syncing."""
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    while True:
        print("\n==========================================================")
        print("   MORSE TLM 1.5 — Universal Data Collection Suite        ")
        print("==========================================================")
        print(f" 💻 Platform : {platform.system()} {platform.machine()}")
        print(f" 📂 Output   : {os.path.abspath(output_dir)}")
        print("----------------------------------------------------------")

        for idx, cat in enumerate(CATEGORIES, 1):
            cat_dir = os.path.join(output_dir, cat)
            count = len([f for f in os.listdir(cat_dir) if f.endswith(".npy")]) if os.path.exists(cat_dir) else 0
            print(f" {idx}. {cat:<24} [{count} samples]")
        print(" 4. Audit & Sync Data to Hugging Face")
        print(" 5. Exit")
        print("----------------------------------------------------------")

        choice = input("Enter choice (1-5): ").strip()
        if choice in ["1", "2", "3"]:
            target_cat = CATEGORIES[int(choice) - 1]
            try:
                cnt_str = input(f"Target NEW sample count for {target_cat} (default 100): ").strip()
                t_count = int(cnt_str) if cnt_str.isdigit() else 100
            except ValueError:
                t_count = 100
            record_category(target_cat, output_dir=output_dir, target_count=t_count)

        elif choice == "4":
            try:
                from data_tools.hf_dataset_sync import push_contributions
                push_contributions(local_folder=output_dir)
            except Exception as e:
                print(f"❌ Sync Error: {e}")

        elif choice == "5":
            print("\n👋 Exiting Universal Data Collector. Happy engineering!\n")
            break
        else:
            print("❌ Invalid selection. Please enter 1, 2, 3, 4, or 5.")


if __name__ == "__main__":
    run_interactive_collector()
