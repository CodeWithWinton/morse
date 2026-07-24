import sounddevice as sd
import numpy as np
import pickle
import time
import os

MODEL_PATH = "model.pkl"
SAMPLE_RATE = 44100

def extract_features(signal):
    sig = signal.flatten()
    max_amp = np.max(np.abs(sig))
    mean_amp = np.mean(np.abs(sig))
    std_amp = np.std(sig)
    zero_crossings = np.sum(np.diff(np.signbit(sig)) != 0)
    
    fft_vals = np.abs(np.fft.rfft(sig))
    fft_peak_freq = np.argmax(fft_vals)
    fft_mean = np.mean(fft_vals)
    fft_std = np.std(fft_vals)
    
    freqs = np.fft.rfftfreq(len(sig), d=1.0/SAMPLE_RATE)
    spectral_centroid = np.sum(freqs * fft_vals) / (np.sum(fft_vals) + 1e-10)
    
    return [max_amp, mean_amp, std_amp, zero_crossings, fft_peak_freq, fft_mean, fft_std, spectral_centroid]

def main():
    if not os.path.exists(MODEL_PATH):
        print("❌ Model not found! Please run 'python3 train_model.py' first.")
        return
        
    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)
        
    clf = model_data["model"]
    categories = model_data["categories"]
    
    print("====================================")
    print("   MORSE - Smart AI Tap Detector    ")
    print("====================================")
    print("🤖 Model Loaded (Noise & Typing Filtering Active)")
    print("🎙️  Listening to chassis... (Tap the metal!)")
    print("Press Ctrl+C to stop.\n")
    
    last_trigger_time = 0
    
    def callback(indata, frames, time_info, status):
        nonlocal last_trigger_time
        volume = np.linalg.norm(indata) * 10
        current_time = time.time()
        
        if volume > 4.5 and (current_time - last_trigger_time > 0.35):
            last_trigger_time = current_time
            features = extract_features(indata)
            
            # Predict category and probability
            prediction_idx = clf.predict([features])[0]
            probs = clf.predict_proba([features])[0]
            confidence = probs[prediction_idx] * 100
            label = categories[prediction_idx]
            
            if label == "tap":
                print(f"🎯 ML VERIFIED CHASSIS TAP! (Confidence: {confidence:.1f}%)")
            elif label == "typing":
                print(f"⌨️  Ignored Keyboard Typing (Vol: {volume:.1f})")
            elif label == "noise":
                print(f"🔕 Ignored Background Noise / Bell (Vol: {volume:.1f})")

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nStopping Smart Detector...")

if __name__ == "__main__":
    main()
