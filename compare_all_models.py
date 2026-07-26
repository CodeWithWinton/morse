import time
import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier, ExtraTreesClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from utils import load_dataset_2d

CATEGORIES = ["left_palm_rest", "right_palm_rest", "palm_resting", "typing", "noise", "desk_tap"]

def main():
    print("==========================================================================")
    print("     MORSE Master AI Benchmark: Normalized Multi-Model Comparison         ")
    print("==========================================================================")
    
    print("\n📊 Loading 2D Spectrogram Dataset (7,967 samples)...")
    X, y = load_dataset_2d(CATEGORIES)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Feature Normalization (StandardScaler: mean=0, std=1)
    scaler = StandardScaler()
    X_train_norm = scaler.fit_transform(X_train)
    X_test_norm = scaler.transform(X_test)
    
    models = {
        "HistGradientBoosting (2D)": HistGradientBoostingClassifier(max_iter=100, learning_rate=0.1, max_leaf_nodes=31, class_weight='balanced', random_state=42),
        "RandomForest (Norm)": RandomForestClassifier(n_estimators=100, max_depth=15, class_weight='balanced', random_state=42, n_jobs=-1),
        "ExtraTrees (Norm)": ExtraTreesClassifier(n_estimators=100, max_depth=15, class_weight='balanced', random_state=42, n_jobs=-1)
    }
    
    results = []
    
    for name, clf in models.items():
        print(f"\n⏳ Training {name}...")
        t0 = time.time()
        
        # Use normalized features for distance/neural models, raw features for HistGradientBoosting
        if "Hist" in name:
            clf.fit(X_train, y_train)
            t_train = (time.time() - t0) * 1000
            acc = clf.score(X_test, y_test)
            y_pred = clf.predict(X_test)
        else:
            clf.fit(X_train_norm, y_train)
            t_train = (time.time() - t0) * 1000
            acc = clf.score(X_test_norm, y_test)
            y_pred = clf.predict(X_test_norm)
            
        rep = classification_report(y_test, y_pred, target_names=CATEGORIES, output_dict=True)
        
        left_rec = rep['left_palm_rest']['recall'] * 100
        right_rec = rep['right_palm_rest']['recall'] * 100
        resting_prec = rep['palm_resting']['precision'] * 100
        
        results.append({
            "name": name,
            "acc": acc * 100,
            "left_rec": left_rec,
            "right_rec": right_rec,
            "resting_prec": resting_prec,
            "time": t_train / 1000
        })
        
    print("\n=========================================================================================================")
    print("                              FEATURE NORMALIZED MULTI-MODEL BENCHMARK RESULTS                           ")
    print("=========================================================================================================")
    print(f"| Model Architecture              | Accuracy | Left Recall | Right Recall | Resting Precision | Training Time |")
    print(f"|---------------------------------|----------|-------------|--------------|-------------------|---------------|")
    for r in results:
        print(f"| {r['name']:31s} | {r['acc']:.1f}%    | {r['left_rec']:.1f}%       | {r['right_rec']:.1f}%        | {r['resting_prec']:.1f}%             | {r['time']:.1f}s         |")
    print("=========================================================================================================")

if __name__ == "__main__":
    main()
