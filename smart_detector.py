import sounddevice as sd
import numpy as np
import pickle
import time
import sys
import os
import actions

import hardware_guards

from utils import extract_features, extract_2d_spectrogram, find_builtin_mic, SAMPLE_RATE, WINDOW_SIZE

MODEL_PATH = "model_2d.pkl" if os.path.exists("model_2d.pkl") else "model.pkl"

def main():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found! Please run 'python3 train_2d_spectrogram_model.py' first.")
        return
        
    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)
        
    clf = model_data["model"]
    categories = model_data["categories"]
    model_name = model_data.get("model_name", "AI Classifier")
    feature_type = model_data.get("feature_type", "1d_fft")
    
    # Start native hardware event guards (Keyboard & Trackpad)
    hardware_guards.start_guards()
    
    # Explicitly find and select Built-in Microphone hardware device
    builtin_device_id, dev_name = find_builtin_mic()
    print(f"🎙️ Target Hardware: [{builtin_device_id}] {dev_name}")

    print("====================================")
    print(f"   MORSE - Smart AI Tap Engine ({model_name})")
    print("====================================")
    print(f"🤖 Stage 1 DSP Filter + Stage 2 ML Classifier ({feature_type.upper()}) Active")
    print("🛡️ Multi-Sensor Guards: Keyboard & Trackpad Active")
    print("💬 Action: Smart WhatsApp Toggle (Open / Hide)")
    print("🎙️  Listening to chassis... (Double-tap metal palm rest!)")
    print("Press Ctrl+C to stop.\n")
    
    last_tap_time = 0
    last_tap_ratio = 0.0
    last_tap_volume = 0.0
    last_tap_centroid = 0.0
    last_action_time = 0.0
    event_counter = 0
    buffer_history = np.zeros(WINDOW_SIZE)
    
    def callback(indata, frames, time_info, status):
        nonlocal last_tap_time, last_tap_ratio, last_tap_volume, last_tap_centroid, last_action_time, event_counter, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()
        
        # Maintain rolling 2048-sample window
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        if 3.2 <= volume <= 85.0:
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
            
            # High-Pass Spectral Ratio (> 2500 Hz)
            hp_energy = np.sum(fft_vals[freqs >= 2500]) + 1e-6
            total_fft_energy = np.sum(fft_vals) + 1e-6
            hp_ratio = hp_energy / total_fft_energy

            # Spectral Centroid Calculation (Hz)
            spectral_centroid = np.sum(freqs * fft_vals) / (total_fft_energy + 1e-6)

            # Pre-Impact Baseline Surge Ratio (Impact energy vs 30ms pre-impact baseline energy)
            pre_impact_start = max(0, peak_idx - 1440) # 30ms pre-impact window at 48kHz
            pre_impact = buffer_history[pre_impact_start:peak_idx]
            pre_rms = np.sqrt(np.mean(pre_impact**2)) + 1e-6 if len(pre_impact) > 0 else 1e-6
            pre_surge_ratio = rms / pre_rms
            
            # Adaptive Pre-Surge: Faint events (< 5.0 Vol) require 2.2x pre-surge proof
            min_pre_surge = 2.2 if volume < 5.0 else 1.8
            is_dsp_candidate = (volume >= 3.2) and (volume <= 85.0) and (crest_factor >= 1.15) and (hp_ratio >= 0.04 or pre_surge_ratio >= min_pre_surge)
            
            if is_dsp_candidate:
                # Stage 2: 2D Spectrogram ML Model Verification
                features = extract_2d_spectrogram(buffer_history) if feature_type == "2d_spectrogram" else extract_features(buffer_history)
                pred_idx = clf.predict([features])[0]
                probs = clf.predict_proba([features])[0]
                confidence = probs[pred_idx] * 100
                predicted_label = categories[pred_idx]
                
                is_valid_tap = predicted_label in ["left_palm_rest", "right_palm_rest", "tap"]
                
                # Dynamic Confidence Threshold: 50% for damped Right Taps, 65% for Left Taps
                min_conf = 50.0 if predicted_label == "right_palm_rest" else 65.0
                
                # Spectral Centroid Consistency Check for Tap 2 (Tolerance < 800 Hz)
                centroid_delta = abs(spectral_centroid - last_tap_centroid)
                is_centroid_match = (last_tap_time == 0) or (centroid_delta < 800.0)
                
                if is_valid_tap and confidence >= min_conf and is_centroid_match:
                    time_since_last = current_time - last_tap_time
                    vol_ratio = volume / (last_tap_volume + 1e-6)
                    
                    # Ignore rebound decay echo (< 100ms) after Tap 1 without resetting state!
                    if time_since_last < 0.10 and last_tap_time > 0:
                        pass
                    elif 0.10 <= time_since_last <= 0.65 and (0.20 <= vol_ratio <= 4.0):
                        # 0.5s Action Debounce Lock: Fast, responsive double-taps
                        if (current_time - last_action_time) >= 0.5:
                            side_str = " (LEFT)" if predicted_label == "left_palm_rest" else (" (RIGHT)" if predicted_label == "right_palm_rest" else "")
                            print(f"\n✌️ DOUBLE-TAP DETECTED!{side_str} (ML Confidence: {confidence:.1f}%, Vol: {volume:.1f})")
                            actions.execute_action("whatsapp")
                            last_action_time = current_time
                        last_tap_time = 0
                        last_tap_ratio = 0.0
                        last_tap_volume = 0.0
                        last_tap_centroid = 0.0
                    else:
                        side_str = " [LEFT]" if predicted_label == "left_palm_rest" else (" [RIGHT]" if predicted_label == "right_palm_rest" else "")
                        print(f" 👆 Tap 1 captured{side_str}... (ML Confidence: {confidence:.1f}%, Vol: {volume:.1f})")
                        last_tap_time = current_time
                        last_tap_ratio = ratio
                        last_tap_volume = volume
                        last_tap_centroid = spectral_centroid
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
