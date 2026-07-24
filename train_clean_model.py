import os
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

DATASET_DIR = "dataset"
CATEGORIES = ["tap", "typing", "noise"]

def extract_features(signal):
    sig = signal.flatten()
    max_amp = np.max(np.abs(sig))
    mean_amp = np.mean(np.abs(sig))
    std_amp = np.std(sig)
    zero_crossings = np.sum(np.diff(np.signbit(sig)) != 0)
    
    fft_vals = np.abs(np.fft.rfft(sig))
    freqs = np.fft.rfftfreq(len(sig), d=1.0/44100)
    
    low_energy = np.sum(fft_vals[(freqs >= 50) & (freqs <= 600)])
    high_energy = np.sum(fft_vals[freqs > 1500]) + 1e-6
    ratio = low_energy / high_energy
    
    rms = np.sqrt(np.mean(sig**2)) + 1e-6
    crest_factor = max_amp / rms
    
    return [max_amp, mean_amp, std_amp, zero_crossings, ratio, crest_factor, low_energy, high_energy]

def main():
    X, y = [], []
    
    for label_idx, cat in enumerate(CATEGORIES):
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy")]
        for f in files:
            signal = np.load(os.path.join(cat_dir, f))
            X.append(extract_features(signal))
            y.append(label_idx)
            
    X = np.array(X)
    y = np.array(y)
    
    print("====================================")
    print("   MORSE - Training Clean ML Model  ")
    print("====================================\n")
    print(f"Total Dataset: {len(X)} samples (238 Silent Taps, 48 Typing, 47 Noise)\n")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"🎯 Random Forest Accuracy: {accuracy * 100:.1f}%\n")
    print(classification_report(y_test, y_pred, target_names=CATEGORIES))
    
    with open("model.pkl", "wb") as f:
        pickle.dump({"model": clf, "categories": CATEGORIES}, f)
    print("✅ Model saved to 'model.pkl'!")

if __name__ == "__main__":
    main()
