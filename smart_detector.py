import sounddevice as sd
import numpy as np
import pickle
import time
import sys
import os
import actions

import hardware_guards
from haptic_feedback import fire_double_tap_confirmation
from utils import extract_lean_305_features, apply_medium_thud_dsp_filter, compute_vibration_trail_ratio, count_impulse_peaks, find_builtin_mic, SAMPLE_RATE

# 350ms Double-Tap Window for snappy physical double-taps
DOUBLE_TAP_WINDOW = 16800
MODEL_PATH = "model_double_tap.pkl" if os.path.exists("model_double_tap.pkl") else "model_2d.pkl"

def main():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found! Please run 'python3 train_double_tap_model.py' first.")
        return
        
    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)
        
    clf = model_data["model"]
    categories = model_data["categories"]
    model_name = model_data.get("model_name", "350ms Double-Tap HistGradientBoosting")
    
    # Start native hardware event guards (Keyboard & Trackpad)
    hardware_guards.start_guards()

    # Explicitly find and select Built-in Microphone hardware device
    builtin_device_id, dev_name = find_builtin_mic()
    print(f"🎙️ Target Hardware: [{builtin_device_id}] {dev_name}")

    print("==========================================================================")
    print("   MORSE - Powered by TLM 1.0 (Tap Learning Model Engine)")
    print("==========================================================================")
    print("🤖 Stage 1 DSP Window + Stage 2 TLM 1.0 Tap Classifier (350ms Window) Active")
    print("🎧 Medium-Tier Impulse Noise Cancellation Active (Strips TV, speech & AC hum)")
    print("🛡️ Multi-Sensor Guards: Keyboard, Trackpad & Control Key Toggle Active")
    print("📳 Haptic Feedback: Trackpad confirmation clicks enabled")
    print("💬 Actions: Left Double-Tap = Toggle WhatsApp | Right Double-Tap = Play/Pause Music")
    print("🎙️  Listening to chassis... (Double-tap left or right metal palm rest!)")
    print("Press Ctrl+C to stop.\n")
    
    last_action_time = 0.0
    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)
    ambient_history = [2.0]
    dynamic_threshold = 3.5

    def callback(indata, frames, time_info, status):
        nonlocal last_action_time, buffer_history, ambient_history, dynamic_threshold
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()

        # Dynamic Noise Floor Auto-Adaptation (Zero Calibration Needed!)
        if volume < 15.0:
            ambient_history.append(volume)
            if len(ambient_history) > 30:
                ambient_history.pop(0)
            dynamic_threshold = max(2.2, np.median(ambient_history) * 2.4)

        # Maintain rolling 350ms window (16,800 samples)
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig

        # Action lockout window (1.20s debounce after triggering an action)
        if (current_time - last_action_time) < 1.20:
            return

        if dynamic_threshold <= volume <= 110.0:
            # 1. Check Hardware Suppression Guards (0% CPU)
            if hardware_guards.is_engine_paused():
                return
            if hardware_guards.is_typing_active(current_time):
                print("   ⌨️  [MORSE GUARD] KEYBOARD BLOCKED (Active typing shield)")
                return
            if hardware_guards.is_trackpad_active(current_time):
                print("   🖱️  [MORSE GUARD] TRACKPAD BLOCKED (Active trackpad shield)")
                return
            
            # 2. Stage 1 Impulse Gate: Verify 2 distinct physical impact peaks in 350ms buffer (Rejects single lid snaps & noise)
            peak_count = count_impulse_peaks(buffer_history)
            if peak_count != 2:
                if "--debug" in sys.argv:
                    print(f"   [🛡️ Impulse Gate Block: Peak Count {peak_count} != 2 (Single Noise / Lid Snap)]")
                return

            # 3. Compute Physical Mechanical Dispersion Ratio on RAW mic buffer
            dispersion_ratio = compute_vibration_trail_ratio(buffer_history)
            if dispersion_ratio < 0.14:
                if "--debug" in sys.argv:
                    print(f"   [🛡️ Physical Fallback Block: Dispersion Ratio {dispersion_ratio:.3f} < 0.14 (Air Snap/Lid Click)]")
                return

            # 3. Medium-Tier Impulse Noise Cancellation & Feature Extraction
            clean_buffer = apply_medium_thud_dsp_filter(buffer_history)
            features = extract_lean_305_features(clean_buffer)

            # 4. ML Model Classification
            probs = clf.predict_proba([features])[0]
            pred_idx = clf.predict([features])[0]
            predicted_label = categories[pred_idx]
            confidence = probs[pred_idx] * 100.0

            # Left-Mic Spatial Proximity Check (Mic is on Left side: Ultra-High Bass >= 0.48 guarantees Left)
            bass_ratio = features[300]
            if bass_ratio >= 0.48 and predicted_label == "double_right_palm":
                predicted_label = "double_left_palm"

            # 5. High-Precision Thresholding (Right >= 85.0%, Left >= 85.0%)
            min_required_conf = 85.0
            
            if predicted_label in ("double_left_palm", "double_right_palm") and confidence >= min_required_conf:
                last_action_time = current_time
                buffer_history.fill(0.0)
                fire_double_tap_confirmation()
                
                if predicted_label == "double_left_palm":
                    print(f"\n✌️ DOUBLE-TAP (LEFT)! (ML Confidence: {confidence:.1f}%, Vol: {volume:.1f})")
                    print("💬 Executing Action: SMART WHATSAPP TOGGLE (OPEN / HIDE)\n")
                    actions.trigger_whatsapp()
                elif predicted_label == "double_right_palm":
                    # Extend lockout to 2.80s for media toggles to shield against speaker audio initialization surge
                    last_action_time = current_time + 1.30
                    print(f"\n✌️ DOUBLE-TAP (RIGHT)! (ML Confidence: {confidence:.1f}%, Vol: {volume:.1f})")
                    print("🎵 Executing Action: APPLE MUSIC PLAY / PAUSE\n")
                    actions.trigger_apple_music_playpause()

    try:
        with sd.InputStream(device=builtin_device_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\n👋 Stopping Smart AI Tap Engine cleanly...")

if __name__ == "__main__":
    main()
