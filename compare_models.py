import os
import time
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

DATASET_DIR = "dataset"
CATEGORIES = ["tap", "typing", "noise"]

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
    print("     MORSE - 3-Class AI Benchmark (TAP vs TYPING vs NOISE)                 ")
    print("==========================================================================\n")
    for idx, cat in enumerate(CATEGORIES):
        count = np.sum(y == idx)
        print(f"  {cat.upper():12s}: {count} samples")
    print(f"\n  TOTAL        : {len(X)} samples\n")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    models = {
        "Extra Trees": ExtraTreesClassifier(n_estimators=200, random_state=42, class_weight='balanced'),
        "Random Forest": RandomForestClassifier(n_estimators=200, random_state=42, class_weight='balanced'),
        "HistGradientBoosting": HistGradientBoostingClassifier(max_iter=200, random_state=42),
        "SVM (RBF)": SVC(kernel='rbf', probability=True, random_state=42, class_weight='balanced'),
        "K-Nearest Neighbors": KNeighborsClassifier(n_neighbors=5),
    }
    
    print(f"{'Model':<25} | {'Accuracy':>10} | {'Precision':>10} | {'Recall':>10} | {'F1 Score':>10} | {'Latency':>12}")
    print("-" * 90)
    
    best_name, best_model, best_f1 = None, None, -1
    results = {}
    
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
        
        print(f"{name:<25} | {acc*100:>9.1f}% | {prec*100:>9.1f}% | {rec*100:>9.1f}% | {f1*100:>9.1f}% | {latency_us:>10.2f} us")
        
        results[name] = {"acc": acc, "f1": f1, "model": clf, "y_pred": y_pred}
        
        if f1 > best_f1:
            best_f1 = f1
            best_name = name
            best_model = clf
            
    print("\n" + "=" * 90)
    print(f"🏆 WINNER: {best_name} (F1 Score: {best_f1*100:.1f}%)")
    print("=" * 90 + "\n")
    
    # Print detailed classification report for the winner
    print(f"--- {best_name} Detailed Classification Report ---\n")
    print(classification_report(y_test, results[best_name]["y_pred"], target_names=CATEGORIES))
    
    # Save the winning model
    with open("model.pkl", "wb") as f:
        pickle.dump({"model": best_model, "categories": CATEGORIES, "model_name": best_name}, f)
    print(f"✅ Saved winning model ({best_name}) to 'model.pkl'!")

if __name__ == "__main__":
    main()
