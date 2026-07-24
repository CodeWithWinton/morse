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
CATEGORIES = ["tap", "typing", "palm_rest", "noise"]

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
        "HistGradientBoosting": HistGradientBoostingClassifier(max_iter=200, random_state=42),
        "Extra Trees": ExtraTreesClassifier(n_estimators=100, random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
    }
    
    print(f"{'Model':<25} | {'80/20 Acc':>10} | {'5-Fold CV F1':>12} | {'Latency':>12}")
    print("-" * 75)
    
    best_name, best_model, best_f1 = None, None, -1
    results = {}
    
    from sklearn.model_selection import StratifiedKFold, cross_val_score
    cv5 = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    for name, clf in models.items():
        print(f"  Training {name}...", end="", flush=True)
        # 5-Fold Cross Validation F1 scores
        cv_scores = cross_val_score(clf, X, y, cv=cv5, scoring='f1_weighted')
        mean_cv_f1 = np.mean(cv_scores) * 100
        std_cv_f1 = np.std(cv_scores) * 100
        
        clf.fit(X_train, y_train)
        
        # Measure Latency (time per prediction)
        start_t = time.perf_counter()
        y_pred = clf.predict(X_test)
        end_t = time.perf_counter()
        
        latency_us = ((end_t - start_t) / len(X_test)) * 1e6
        acc = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
        
        print(f"\r{name:<25} | {acc*100:>9.1f}% | {mean_cv_f1:>7.1f}% ± {std_cv_f1:.1f}% | {latency_us:>10.2f} us")
        
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
