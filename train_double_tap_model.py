import pickle
import time
import os
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report

from utils import extract_lean_305_features, SAMPLE_RATE

DATASET_DIR = "dataset_double_taps"
CATEGORIES = ["double_left_palm", "double_right_palm", "noise_and_typing"]
MODEL_PATH = "model_double_tap.pkl"

H5_FILEPATH = "morse_dataset.h5"

def _process_sample(args):
    signal, label_idx, is_tap = args
    out = [(extract_lean_305_features(signal), label_idx)]
    if is_tap:
        out.append((extract_lean_305_features(signal * 1.20), label_idx))
        out.append((extract_lean_305_features(signal * 0.80), label_idx))
    return out

def load_double_tap_dataset():
    import multiprocessing
    X, y = [], []
    
    # 1. Primary: Ultra-Fast HDF5 Loading (morse_dataset.h5)
    if os.path.exists(H5_FILEPATH):
        import h5py
        print(f"📄 Loading primary dataset from '{H5_FILEPATH}'...")
        tasks = []
        with h5py.File(H5_FILEPATH, "r") as h5f:
            for label_idx, cat in enumerate(CATEGORIES):
                if cat in h5f:
                    samples = h5f[cat][:]
                    is_tap = cat in ("double_left_palm", "double_right_palm")
                    print(f"  • HDF5: Preparing {len(samples):4d} samples for '{cat.upper()}'...")
                    for s in samples:
                        tasks.append((s.astype(np.float32), label_idx, is_tap))
                        
        print(f"⚡ Extracting 310D features in parallel across {multiprocessing.cpu_count()} CPU cores...")
        t0 = time.time()
        with multiprocessing.Pool() as pool:
            batch_results = pool.map(_process_sample, tasks)
            
        for res_list in batch_results:
            for feat, label in res_list:
                X.append(feat)
                y.append(label)
                
        print(f"✅ Extracted {len(X)} augmented feature vectors in {time.time() - t0:.2f}s!")
        return np.array(X), np.array(y)

    # 2. Fallback: Standard .npy Folder Loading (dataset_double_taps)
    print(f"📁 Loading fallback dataset from '{DATASET_DIR}/'...")
    for label_idx, cat in enumerate(CATEGORIES):
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy")]
        print(f"  • .npy: Loading {len(files):4d} samples for '{cat.upper()}'...")
        
        for f in files:
            filepath = os.path.join(cat_dir, f)
            signal = np.load(filepath).astype(np.float32)
            
            feat = extract_lean_305_features(signal)
            X.append(feat)
            y.append(label_idx)
            
            if cat in ("double_left_palm", "double_right_palm"):
                X.append(extract_lean_305_features(signal * 1.20))
                y.append(label_idx)
                X.append(extract_lean_305_features(signal * 0.80))
                y.append(label_idx)
                
    return np.array(X), np.array(y)

def main():
    print("==========================================================================")
    print("     MORSE - 500ms Double-Tap Native AI Model Trainer                     ")
    print("==========================================================================")
    
    if not os.path.exists(DATASET_DIR):
        print(f"❌ Dataset directory '{DATASET_DIR}' not found!")
        return
        
    X, y = load_double_tap_dataset()
    if len(X) == 0:
        print("❌ No samples found in dataset!")
        return
        
    print(f"\n  TOTAL AUGMENTED SAMPLES: {len(X)}")
    print(f"  FEATURE MATRIX SHAPE   : {X.shape}")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    
    print("\n⏳ Running 5-Fold Stratified Cross-Validation...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        clf_fold = HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.08,
            max_leaf_nodes=45,
            class_weight='balanced',
            random_state=42
        )
        clf_fold.fit(X[train_idx], y[train_idx])
        score = clf_fold.score(X[val_idx], y[val_idx])
        cv_scores.append(score)
        print(f"  ⚡ Fold {fold}/5: {score*100:.1f}% Accuracy")
        
    print(f"\n🏆 Mean Cross-Validation Accuracy: {np.mean(cv_scores)*100:.1f}% (+/- {np.std(cv_scores)*100:.1f}%)")
    
    print("\n⏳ Fitting Production Model on Train Split...")
    clf = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.08,
        max_leaf_nodes=45,
        class_weight='balanced',
        random_state=42
    )
    t0 = time.time()
    clf.fit(X_train, y_train)
    t_train = (time.time() - t0) * 1000
    
    acc = clf.score(X_test, y_test)
    y_pred = clf.predict(X_test)
    
    print(f"\n✅ Training Completed in {t_train:.1f}ms!")
    print(f"🎯 Test Set Accuracy: {acc*100:.1f}%\n")
    print(classification_report(y_test, y_pred, target_names=CATEGORIES))
    
    model_data = {
        "model": clf,
        "categories": CATEGORIES,
        "model_name": "500ms Double-Tap HistGradientBoosting",
        "feature_type": "lean_305_double_tap"
    }
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model_data, f)
        
    print(f"✅ Successfully saved double-tap model to '{MODEL_PATH}'!")

if __name__ == "__main__":
    main()
