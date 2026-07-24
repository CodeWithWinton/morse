import os
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

DATASET_DIR = "dataset"
CATEGORIES = ["tap", "typing", "noise"]

def extract_features(signal):
    """
    Extract key time-domain and frequency-domain features from raw audio signal.
    """
    sig = signal.flatten()
    
    # 1. Time-Domain Features
    max_amp = np.max(np.abs(sig))
    mean_amp = np.mean(np.abs(sig))
    std_amp = np.std(sig)
    zero_crossings = np.sum(np.diff(np.signbit(sig)) != 0)
    
    # 2. Frequency-Domain Features (FFT)
    fft_vals = np.abs(np.fft.rfft(sig))
    fft_peak_freq = np.argmax(fft_vals)
    fft_mean = np.mean(fft_vals)
    fft_std = np.std(fft_vals)
    
    # Spectral Centroid approximation
    freqs = np.fft.rfftfreq(len(sig), d=1.0/44100)
    spectral_centroid = np.sum(freqs * fft_vals) / (np.sum(fft_vals) + 1e-10)
    
    return [max_amp, mean_amp, std_amp, zero_crossings, fft_peak_freq, fft_mean, fft_std, spectral_centroid]

def main():
    X = []
    y = []
    
    print("====================================")
    print("   MORSE - Training ML Model        ")
    print("====================================\n")
    
    for label_idx, cat in enumerate(CATEGORIES):
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        
        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy")]
        print(f"Loading {len(files)} samples for category: '{cat}'...")
        
        for f in files:
            filepath = os.path.join(cat_dir, f)
            signal = np.load(filepath)
            features = extract_features(signal)
            X.append(features)
            y.append(label_idx)
            
    # Synthetic Data Augmentation: Mix Taps with Background Noise & Typing
    taps = [X[i] for i in range(len(X)) if y[i] == 0]
    noises = [X[i] for i in range(len(X)) if y[i] == 2]
    typings = [X[i] for i in range(len(X)) if y[i] == 1]
    
    # Generate augmented tap+noise samples
    augmented_taps = []
    for tap_sig in [np.load(os.path.join(DATASET_DIR, "tap", f)) for f in os.listdir(os.path.join(DATASET_DIR, "tap")) if f.endswith(".npy")]:
        for noise_sig in [np.load(os.path.join(DATASET_DIR, "noise", f)) for f in os.listdir(os.path.join(DATASET_DIR, "noise"))[:10] if f.endswith(".npy")]:
            mixed = tap_sig + 0.5 * noise_sig
            X.append(extract_features(mixed))
            y.append(0)  # Still a valid tap!
            
        for type_sig in [np.load(os.path.join(DATASET_DIR, "typing", f)) for f in os.listdir(os.path.join(DATASET_DIR, "typing"))[:10] if f.endswith(".npy")]:
            mixed = tap_sig + 0.5 * type_sig
            X.append(extract_features(mixed))
            y.append(0)  # Still a valid tap!
            
    X = np.array(X)
    y = np.array(y)
    
    print(f"\nTotal Dataset (with Augmentation): {len(X)} samples across {len(CATEGORIES)} categories.")
    
    if len(X) < 10:
        print("❌ Not enough samples to train! Please collect more data.")
        return
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training Random Forest Classifier...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n🎯 Model Accuracy: {accuracy * 100:.1f}%\n")
    print(classification_report(y_test, y_pred, target_names=CATEGORIES))
    
    # Save trained model and metadata
    model_data = {
        "model": clf,
        "categories": CATEGORIES
    }
    
    with open("model.pkl", "wb") as f:
        pickle.dump(model_data, f)
        
    print("✅ Model successfully saved to 'model.pkl'!")

if __name__ == "__main__":
    main()
