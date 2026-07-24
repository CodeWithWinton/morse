import os
import time
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

DATASET_DIR = "dataset"
CATEGORIES = ["tap", "typing", "noise"]

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
    
    freqs = np.fft.rfftfreq(len(sig), d=1.0/44100)
    spectral_centroid = np.sum(freqs * fft_vals) / (np.sum(fft_vals) + 1e-10)
    
    return [max_amp, mean_amp, std_amp, zero_crossings, fft_peak_freq, fft_mean, fft_std, spectral_centroid]

def main():
    X, y = [], []
    
    for label_idx, cat in enumerate(CATEGORIES):
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        for f in os.listdir(cat_dir):
            if f.endswith(".npy"):
                signal = np.load(os.path.join(cat_dir, f))
                X.append(extract_features(signal))
                y.append(label_idx)
                
    # Data Augmentation
    for tap_sig in [np.load(os.path.join(DATASET_DIR, "tap", f)) for f in os.listdir(os.path.join(DATASET_DIR, "tap")) if f.endswith(".npy")]:
        for noise_sig in [np.load(os.path.join(DATASET_DIR, "noise", f)) for f in os.listdir(os.path.join(DATASET_DIR, "noise"))[:10] if f.endswith(".npy")]:
            X.append(extract_features(tap_sig + 0.5 * noise_sig))
            y.append(0)
        for type_sig in [np.load(os.path.join(DATASET_DIR, "typing", f)) for f in os.listdir(os.path.join(DATASET_DIR, "typing"))[:10] if f.endswith(".npy")]:
            X.append(extract_features(tap_sig + 0.5 * type_sig))
            y.append(0)
            
    X = np.array(X)
    y = np.array(y)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    models = {
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
        "Extra Trees": ExtraTreesClassifier(n_estimators=100, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, random_state=42, eval_metric='mlogloss'),
        "Support Vector Machine (RBF)": SVC(kernel='rbf', probability=True, random_state=42),
        "K-Nearest Neighbors (K=3)": KNeighborsClassifier(n_neighbors=3),
        "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42)
    }
    
    print("==========================================================================")
    print("           MORSE - Machine Learning Model Benchmark                       ")
    print("==========================================================================\n")
    print(f"{'Model':<30} | {'Accuracy':<10} | {'Precision':<10} | {'Recall':<10} | {'Latency (us)':<12}")
    print("-" * 82)
    
    best_name, best_model, best_f1 = None, None, -1
    
    for name, clf in models.items():
        clf.fit(X_train, y_train)
        
        # Measure Latency (time per prediction)
        start_t = time.perf_counter()
        y_pred = clf.predict(X_test)
        end_t = time.perf_counter()
        
        latency_us = ((end_t - start_t) / len(X_test)) * 1e6
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        rec = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        print(f"{name:<30} | {acc*100:>8.1f}% | {prec*100:>8.1f}% | {rec*100:>8.1f}% | {latency_us:>10.2f} us")
        
        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = clf
            
    print("\n" + "=" * 82)
    print(f"🏆 WINNER: {best_name} (F1 Score: {best_f1*100:.1f}%)")
    print("=" * 82 + "\n")
    
    # Save the winning model
    with open("model.pkl", "wb") as f:
        pickle.dump({"model": best_model, "categories": CATEGORIES, "model_name": best_name}, f)
    print(f"✅ Saved winning model ({best_name}) to 'model.pkl'!")

if __name__ == "__main__":
    main()
