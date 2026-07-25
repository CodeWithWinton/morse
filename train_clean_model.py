import os
import numpy as np
import pickle
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

DATASET_DIR = "dataset"
CATEGORIES = ["tap", "typing", "desk_tap", "palm_rest", "noise"]

def extract_features(signal):
    sig = signal.flatten()
    max_amp = np.max(np.abs(sig))
    rms = np.sqrt(np.mean(sig**2)) + 1e-6
    crest_factor = max_amp / rms
    
    fft_vals = np.abs(np.fft.rfft(sig))
    fft_norm = fft_vals / (np.max(fft_vals) + 1e-6)
    
    return np.concatenate([[max_amp, crest_factor], fft_norm])

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
    
    print("==========================================================================")
    print("     MORSE - Fast 4-Class AI Model Trainer                               ")
    print("==========================================================================\n")
    for idx, cat in enumerate(CATEGORIES):
        count = np.sum(y == idx)
        print(f"  {cat.upper():12s}: {count} samples")
    print(f"\n  TOTAL        : {len(X)} samples\n")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    clf = HistGradientBoostingClassifier(max_iter=200, random_state=42)
    print("⏳ Training HistGradientBoosting...", end="", flush=True)
    clf.fit(X_train, y_train)
    print(" DONE! ✅\n")
    
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    
    print(f"🎯 Model Accuracy: {acc * 100:.1f}%\n")
    print(classification_report(y_test, y_pred, target_names=CATEGORIES))
    
    with open("model.pkl", "wb") as f:
        pickle.dump({"model": clf, "categories": CATEGORIES, "model_name": "HistGradientBoosting"}, f)
    print("✅ Successfully saved 4-class winning model to 'model.pkl'!")

if __name__ == "__main__":
    main()
