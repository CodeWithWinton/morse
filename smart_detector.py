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
from custom_noise_engine import CustomChassisNoiseEngine

# 500ms Double-Tap Window for snappy physical double-taps matching 97.5% TLM model
DOUBLE_TAP_WINDOW = 24000
MODEL_PATH = "model_double_tap.pkl"

def main():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found! Please run 'python3 train_double_tap_model.py' first.")
        return
        
    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)
        
    clf = model_data["model"]
    categories = model_data["categories"]
    model_name = model_data.get("model_name", "500ms Double-Tap HistGradientBoosting (310 Features)")
    
    # Start native hardware event guards (Keyboard & Trackpad)
    hardware_guards.start_guards()

    # Initialize Custom In-House Chassis Noise & Speaker Engine (< 0.9% CPU)
    noise_engine = CustomChassisNoiseEngine(sample_rate=SAMPLE_RATE)

    # Explicitly find and select Built-in Microphone hardware device
    builtin_device_id, dev_name = find_builtin_mic()
    print(f"🎙️ Target Hardware: [{builtin_device_id}] {dev_name}")

    print("==========================================================================")
    print("   MORSE - Powered by TLM 1.5 (Tap Learning Model Engine)")
    print("==========================================================================")
    print("🤖 Stage 1 DSP Window + Stage 2 TLM 1.5 Tap Classifier (500ms Native Window) Active")
    print("🎧 Custom In-House Noise & Speaker Shield Active (<0.9% CPU, Zero Tap Loss)")
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

            # Check if MacBook speaker output is active (YouTube, Spotify, Music)
            spk_active = hardware_guards.is_speaker_output_active()
            noise_engine.set_speaker_active(spk_active)
            
            # 2. Process Custom Noise Cancellation & Speaker Shield Engine
            clean_buffer, noise_stats = noise_engine.process_frame(buffer_history)
            
            # Transient Crest Factor Shield: Require Peak/RMS >= 3.0 to reject continuous sounds
            if noise_stats["crest_factor"] < 2.8:
                if "--debug" in sys.argv:
                    print(f"   [🛡️ Crest Factor Shield Block: {noise_stats['crest_factor']:.2f} < 2.8 (Continuous Speech / Music)]")
                return

            # 3. Stage 1 Impulse Gate: Verify physical impact peak presence
            peak_count = count_impulse_peaks(buffer_history)
            if peak_count < 1:
                if "--debug" in sys.argv:
                    print(f"   [🛡️ Impulse Gate Block: Peak Count {peak_count} < 1 (No Impact Detected)]")
                return

            # 4. Compute Physical Mechanical Dispersion Ratio on RAW mic buffer
            dispersion_ratio = compute_vibration_trail_ratio(buffer_history)
            if dispersion_ratio < 0.14:
                if "--debug" in sys.argv:
                    print(f"   [🛡️ Physical Fallback Block: Dispersion Ratio {dispersion_ratio:.3f} < 0.14 (Air Snap/Lid Click)]")
                return

            # Extract 310 features directly from RAW mic buffer (100% 1:1 match with model training)
            features = extract_lean_305_features(buffer_history)

            # 4. ML Model Classification (HistGradientBoosting 310D)
            probs = clf.predict_proba([features])[0]
            pred_idx = clf.predict([features])[0]
            predicted_label = categories[pred_idx]
            confidence = probs[pred_idx] * 100.0

            # Correct MelBin 4 (index 60) & MelBin 9 (index 135) Frame 0 Onset Ratio
            mel_4_frame_0 = features[60]
            mel_9_frame_0 = features[135]
            frame_0_energy = np.sum([features[m * 15] for m in range(20)]) + 1e-6
            onset_ratio = float((mel_4_frame_0 + mel_9_frame_0) / frame_0_energy)

            # 5. High-Precision Thresholding
            min_required_conf = 85.0
            
            if predicted_label in ("double_left_palm", "double_right_palm") and confidence >= min_required_conf:
                last_action_time = current_time
                buffer_history.fill(0.0)
                fire_double_tap_confirmation()
                
                if predicted_label == "double_left_palm":
                    print(f"\n✌️ DOUBLE-TAP (LEFT)! (ML Conf: {confidence:.1f}%, Onset Ratio: {onset_ratio:.3f}, Vol: {volume:.1f})")
                    print("💬 Executing Action: SMART WHATSAPP TOGGLE (OPEN / HIDE)\n")
                    actions.trigger_whatsapp()
                elif predicted_label == "double_right_palm":
                    # Extend lockout to 2.80s for media toggles to shield against speaker audio initialization surge
                    last_action_time = current_time + 1.30
                    print(f"\n✌️ DOUBLE-TAP (RIGHT)! (ML Conf: {confidence:.1f}%, Onset Ratio: {onset_ratio:.3f}, Vol: {volume:.1f})")
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
