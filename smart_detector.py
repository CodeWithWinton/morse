import sounddevice as sd
import numpy as np
import pickle
import time
import sys
import os
import actions

import hardware_guards
from haptic_feedback import fire_double_tap_confirmation
from utils import extract_lean_305_features, find_builtin_mic, SAMPLE_RATE

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
    print(f"   MORSE - 350ms Double-Tap Native AI Engine ({model_name})")
    print("==========================================================================")
    print("🤖 Stage 1 DSP Window + Stage 2 ML Double-Tap Classifier (350ms Window) Active")
    print("🛡️ Multi-Sensor Guards: Keyboard, Trackpad & Control Key Toggle Active")
    print("📳 Haptic Feedback: Trackpad confirmation clicks enabled")
    print("💬 Actions: Left Double-Tap = Toggle WhatsApp | Right Double-Tap = Play/Pause Music")
    print("🎙️  Listening to chassis... (Double-tap left or right metal palm rest!)")
    print("Press Ctrl+C to stop.\n")
    
    last_action_time = 0.0
    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)

    def callback(indata, frames, time_info, status):
        nonlocal last_action_time, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()

        # Maintain rolling 350ms window (16,800 samples)
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig

        # Action lockout window (1.20s debounce after triggering an action)
        if (current_time - last_action_time) < 1.20:
            return

        if 2.2 <= volume <= 110.0:
            # 1. Check Hardware Suppression Guards (0% CPU)
            if hardware_guards.is_engine_paused():
                return
            if hardware_guards.is_typing_active(current_time):
                print("   ⌨️  [MORSE GUARD] KEYBOARD BLOCKED (Active typing shield)")
                return
            if hardware_guards.is_trackpad_active(current_time):
                print("   🖱️  [MORSE GUARD] TRACKPAD BLOCKED (Active trackpad shield)")
                return
            
            # 2. Extract 305 features over the 500ms double-tap gesture window
            features = extract_lean_305_features(buffer_history)
            bass_ratio = features[300]  # Scalar 300 is 120-600Hz Bass Energy Ratio
            
            # 3. ML Model Classification
            probs = clf.predict_proba([features])[0]
            pred_idx = clf.predict([features])[0]
            predicted_label = categories[pred_idx]
            confidence = probs[pred_idx] * 100.0

            # 4. High-Precision Thresholding (Right >= 85.0%, Left >= 85.0%)
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
