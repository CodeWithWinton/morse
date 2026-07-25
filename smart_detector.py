import sounddevice as sd
import numpy as np
import pickle
import time
import os
import actions

MODEL_PATH = "model.pkl"
SAMPLE_RATE = 44100

MODEL_PATH = "model.pkl"
SAMPLE_RATE = 44100
WINDOW_SIZE = 2048

def extract_features(signal):
    sig = signal.flatten()
    max_amp = np.max(np.abs(sig))
    rms = np.sqrt(np.mean(sig**2)) + 1e-6
    crest_factor = max_amp / rms
    
    fft_vals = np.abs(np.fft.rfft(sig))
    fft_norm = fft_vals / (np.max(fft_vals) + 1e-6)
    
    return np.concatenate([[max_amp, crest_factor], fft_norm])

def main():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found! Please run 'python3 compare_models.py' first.")
        return
        
    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)
        
    clf = model_data["model"]
    categories = model_data["categories"]
    model_name = model_data.get("model_name", "AI Classifier")
    
    # Explicitly find and select Built-in Microphone hardware device
    devices = sd.query_devices()
    builtin_device_id = None
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and ("built-in" in dev['name'].lower() or "macbook" in dev['name'].lower()):
            builtin_device_id = i
            print(f"🎙️ Target Hardware: [{i}] {dev['name']}")
            break

    print("====================================")
    print(f"   MORSE - Smart AI Tap Engine ({model_name})")
    print("====================================")
    print("🤖 Stage 1 DSP Filter + Stage 2 ML Classifier Active")
    print("💬 Action: Smart WhatsApp Toggle (Open / Hide)")
    print("🎙️  Listening to chassis... (Double-tap metal palm rest!)")
    print("Press Ctrl+C to stop.\n")
    
    last_tap_time = 0
    last_tap_ratio = 0.0
    event_counter = 0
    buffer_history = np.zeros(WINDOW_SIZE)
    
    def callback(indata, frames, time_info, status):
        nonlocal last_tap_time, last_tap_ratio, event_counter, buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10
        current_time = time.time()
        
        # Maintain rolling 2048-sample window
        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig
        
        if 10.0 <= volume <= 70.0:
            event_counter += 1
            
            # Stage 1: Fast DSP Filter
            peak_idx = np.argmax(np.abs(sig))
            start_idx = max(0, peak_idx - 50)
            end_idx = min(len(sig), peak_idx + 800)
            transient = sig[start_idx:end_idx]
            
            fft_vals = np.abs(np.fft.rfft(transient))
            freqs = np.fft.rfftfreq(len(transient), d=1.0/SAMPLE_RATE)
            
            bass_energy = np.sum(fft_vals[(freqs >= 120) & (freqs <= 600)])
            high_energy = np.sum(fft_vals[freqs > 1500]) + 1e-6
            ratio = bass_energy / high_energy
            
            rms = np.sqrt(np.mean(transient**2)) + 1e-6
            peak = np.max(np.abs(transient))
            crest_factor = peak / rms
            
            is_dsp_candidate = (10.0 <= volume <= 70.0) and (ratio >= 0.50) and (crest_factor >= 1.2)
            
            if is_dsp_candidate:
                # Stage 2: ML Model Verification
                features = extract_features(buffer_history)
                pred_idx = clf.predict([features])[0]
                probs = clf.predict_proba([features])[0]
                confidence = probs[pred_idx] * 100
                predicted_label = categories[pred_idx]
                
                if predicted_label == "tap" and confidence >= 70.0:
                    time_since_last = current_time - last_tap_time
                    if 0.06 < time_since_last < 0.60:
                        print(f"\n✌️ DOUBLE-TAP DETECTED! (ML Confidence: {confidence:.1f}%, Vol: {volume:.1f})")
                        actions.execute_action("whatsapp")
                        last_tap_time = 0
                        last_tap_ratio = 0.0
                    elif time_since_last <= 0.05 and last_tap_time > 0:
                        pass
                    else:
                        print(f" 👆 Tap 1 captured... (ML Confidence: {confidence:.1f}%, Vol: {volume:.1f})")
                        last_tap_time = current_time
                        last_tap_ratio = ratio
                else:
                    if predicted_label == "tap":
                        print(f"   [Low Confidence Tap: {confidence:.1f}%] Event #{event_counter:03d}")
                    else:
                        icon = "⌨️" if predicted_label == "typing" else "🔕"
                        print(f"   [{icon} ML Blocked: {predicted_label.upper()}] Event #{event_counter:03d} (Conf: {confidence:.1f}%)")
                    last_tap_time = 0
                    last_tap_ratio = 0.0
            else:
                print(f"   [DSP Filtered] Event #{event_counter:03d} -> Ratio: {ratio:.2f}, Vol: {volume:.1f}")

    try:
        with sd.InputStream(device=builtin_device_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 Stopping Smart AI Tap Engine cleanly...")

if __name__ == "__main__":
    main()
