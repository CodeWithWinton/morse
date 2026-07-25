import sounddevice as sd
import numpy as np
import pickle
import time
import sys
import os
import actions

import hardware_guards

from utils import extract_features, find_builtin_mic, SAMPLE_RATE, WINDOW_SIZE

MODEL_PATH = "model.pkl"

def main():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found! Please run 'python3 compare_models.py' first.")
        return
        
    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)
        
    clf = model_data["model"]
    categories = model_data["categories"]
    model_name = model_data.get("model_name", "AI Classifier")
    
    # Start native hardware event guards (Keyboard & Trackpad)
    hardware_guards.start_guards()
    
    # Explicitly find and select Built-in Microphone hardware device
    builtin_device_id, dev_name = find_builtin_mic()
    print(f"🎙️ Target Hardware: [{builtin_device_id}] {dev_name}")

    print("====================================")
    print(f"   MORSE - Smart AI Tap Engine ({model_name})")
    print("====================================")
    print("🤖 Stage 1 DSP Filter + Stage 2 ML Classifier Active")
    print("🛡️ Multi-Sensor Guards: Keyboard & Trackpad Active")
    print("💬 Action: Smart WhatsApp Toggle (Open / Hide)")
    print("🎙️  Listening to chassis... (Double-tap metal palm rest!)")
    print("Press Ctrl+C to stop.\n")
    
    last_tap_time = 0
    last_tap_ratio = 0.0
    last_tap_volume = 0.0
    last_action_time = 0.0
    event_counter = 0
    buffer_history = np.zeros(WINDOW_SIZE)
    
    def callback(indata, frames, time_info, status):
        nonlocal last_tap_time, last_tap_ratio, last_tap_volume, last_action_time, event_counter, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()
        
        # Maintain rolling 2048-sample window
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        if 3.5 <= volume <= 85.0:
            event_counter += 1
            
            # Check Hardware Suppression Guards (0% CPU)
            if hardware_guards.is_typing_active(current_time):
                if "--debug" in sys.argv:
                    print(f"   [⌨️ Hardware Blocked: TYPING] Event #{event_counter:03d}")
                last_tap_time = 0
                return
            if hardware_guards.is_trackpad_active(current_time):
                if "--debug" in sys.argv:
                    print(f"   [🖱️ Hardware Blocked: TRACKPAD] Event #{event_counter:03d}")
                last_tap_time = 0
                return
            
            # Stage 1: Fast DSP Filter (Sliced from rolling 2048-sample buffer_history to prevent boundary truncation!)
            peak_idx = np.argmax(np.abs(buffer_history))
            start_idx = max(0, peak_idx - 100)
            end_idx = min(len(buffer_history), peak_idx + 1000)
            transient = buffer_history[start_idx:end_idx]
            
            fft_vals = np.abs(np.fft.rfft(transient))
            freqs = np.fft.rfftfreq(len(transient), d=1.0/SAMPLE_RATE)
            
            bass_energy = np.sum(fft_vals[(freqs >= 120) & (freqs <= 600)])
            high_energy = np.sum(fft_vals[freqs > 1500]) + 1e-6
            ratio = bass_energy / high_energy
            
            rms = np.sqrt(np.mean(transient**2)) + 1e-6
            peak = np.max(np.abs(transient))
            crest_factor = peak / rms
            
            # High-Pass Spectral Ratio (> 2500 Hz) to eliminate speaker music & airborne vocal speech
            hp_energy = np.sum(fft_vals[freqs >= 2500]) + 1e-6
            total_fft_energy = np.sum(fft_vals) + 1e-6
            hp_ratio = hp_energy / total_fft_energy
            
            # Distance-Aware Dynamic Volume Floor:
            # Right taps have lower high-frequency ratio (damped across chassis) -> floor 3.5
            # Left taps have higher high-frequency ratio -> floor 4.8
            min_vol = 3.5 if hp_ratio < 0.25 else 4.8
            
            is_dsp_candidate = (volume >= min_vol) and (volume <= 85.0) and (crest_factor >= 1.18) and (hp_ratio >= 0.06)
            
            if is_dsp_candidate:
                # Stage 2: ML Model Verification
                features = extract_features(buffer_history)
                pred_idx = clf.predict([features])[0]
                probs = clf.predict_proba([features])[0]
                confidence = probs[pred_idx] * 100
                predicted_label = categories[pred_idx]
                
                if predicted_label == "tap" and confidence >= 70.0:
                    time_since_last = current_time - last_tap_time
                    vol_ratio = volume / (last_tap_volume + 1e-6)
                    
                    # Ignore rebound decay echo (< 100ms) after Tap 1 without resetting state!
                    if time_since_last < 0.10 and last_tap_time > 0:
                        pass
                    elif 0.10 <= time_since_last <= 0.65 and (0.35 <= vol_ratio <= 2.80):
                        # 1.0s Action Debounce Lock: Prevents rapid double-toggling (open/close loop)
                        if (current_time - last_action_time) >= 1.0:
                            print(f"\n✌️ DOUBLE-TAP DETECTED! (ML Confidence: {confidence:.1f}%, Vol: {volume:.1f})")
                            actions.execute_action("whatsapp")
                            last_action_time = current_time
                        last_tap_time = 0
                        last_tap_ratio = 0.0
                        last_tap_volume = 0.0
                    else:
                        if time_since_last > 0.65 or last_tap_time == 0:
                            print(f" 👆 Tap 1 captured... (ML Confidence: {confidence:.1f}%, Vol: {volume:.1f})")
                            last_tap_time = current_time
                            last_tap_ratio = ratio
                            last_tap_volume = volume
                        else:
                            if "--debug" in sys.argv:
                                print(f"   [Volume Mismatch Blocked: Vol {volume:.1f} vs Tap1 {last_tap_volume:.1f}] Event #{event_counter:03d}")
                            last_tap_time = 0
                            last_tap_ratio = 0.0
                            last_tap_volume = 0.0
                else:
                    if "--debug" in sys.argv:
                        if predicted_label == "tap":
                            print(f"   [Low Confidence Tap: {confidence:.1f}%] Event #{event_counter:03d}")
                        else:
                            icons = {"typing": "⌨️", "desk_tap": "🪵", "palm_rest": "✋", "noise": "🔕"}
                            icon = icons.get(predicted_label, "🔕")
                            print(f"   [{icon} ML Blocked: {predicted_label.upper()}] Event #{event_counter:03d} (Conf: {confidence:.1f}%)")
                    last_tap_time = 0
                    last_tap_ratio = 0.0
                    last_tap_volume = 0.0
            else:
                if "--debug" in sys.argv:
                    print(f"   [DSP Filtered] Event #{event_counter:03d} -> Ratio: {ratio:.2f}, Vol: {volume:.1f}")

    try:
        with sd.InputStream(device=builtin_device_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 Stopping Smart AI Tap Engine cleanly...")

if __name__ == "__main__":
    main()
