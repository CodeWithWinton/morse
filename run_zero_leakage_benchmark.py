import h5py
import time
import os
import numpy as np
import multiprocessing
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from utils import extract_lean_305_features

CATEGORIES = ['double_left_palm', 'double_right_palm', 'noise_and_typing']
H5_FILEPATH = 'morse_dataset.h5'

def _extract_single(args):
    sig, label_idx = args
    return extract_lean_305_features(sig), label_idx

def _extract_train_aug(args):
    sig, label_idx = args
    is_tap = label_idx in (0, 1)
    feats = [(extract_lean_305_features(sig), label_idx)]
    if is_tap:
        feats.append((extract_lean_305_features(sig * 1.10), label_idx))
        feats.append((extract_lean_305_features(sig * 0.90), label_idx))
    return feats

def main():
    print("==========================================================================")
    print("      MORSE - 8-CORE PARALLEL ZERO-LEAKAGE REAL-WORLD BENCHMARK          ")
    print("==========================================================================")
    
    raw_samples, raw_labels = [], []
    with h5py.File(H5_FILEPATH, 'r') as h5f:
        for label_idx, cat in enumerate(CATEGORIES):
            if cat in h5f:
                samples = h5f[cat][:]
                print(f" • Loaded {len(samples):5d} raw samples for '{cat.upper()}'...")
                for s in samples:
                    raw_samples.append(s.astype(np.float32))
                    raw_labels.append(label_idx)

    raw_samples = np.array(raw_samples, dtype=object)
    raw_labels = np.array(raw_labels)

    # 1. SPLIT RAW SAMPLES BEFORE AUGMENTATION (ZERO LEAKAGE)
    raw_train, raw_test, y_train_raw, y_test_raw = train_test_split(
        raw_samples, raw_labels, test_size=0.20, random_state=42, stratify=raw_labels
    )

    print(f"\n🔒 Split: {len(raw_train)} Raw Train Samples | {len(raw_test)} Raw Test Samples (100% Unseen)")

    num_cores = multiprocessing.cpu_count()
    print(f"⚡ Parallel extraction across {num_cores} CPU cores...")
    t0 = time.time()

    with multiprocessing.Pool(num_cores) as pool:
        test_tasks = [(raw_test[i], y_test_raw[i]) for i in range(len(raw_test))]
        test_results = pool.map(_extract_single, test_tasks)
        
        train_tasks = [(raw_train[i], y_train_raw[i]) for i in range(len(raw_train))]
        train_results = pool.map(_extract_train_aug, train_tasks)

    X_test = np.array([f for f, l in test_results])
    y_test = np.array([l for f, l in test_results])

    X_train, y_train = [], []
    for res_list in train_results:
        for f, l in res_list:
            X_train.append(f)
            y_train.append(l)

    X_train = np.array(X_train)
    y_train = np.array(y_train)

    print(f"✅ Extracted Feature Matrices in {time.time() - t0:.2f}s!")
    print(f"   Train Matrix: {X_train.shape} | Test Matrix: {X_test.shape}")

    print("\n🧠 Training HistGradientBoostingClassifier on Zero-Leakage Dataset...")
    clf = HistGradientBoostingClassifier(max_iter=200, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    print(f"\n🎯 ZERO-LEAKAGE UNSEEN TEST ACCURACY: {acc*100:.2f}%\n")
    print("=== CLASSIFICATION REPORT ===")
    print(classification_report(y_test, y_pred, target_names=CATEGORIES, digits=4))
    print("=== CONFUSION MATRIX ===")
    print(f"Categories: {CATEGORIES}")
    print(cm)

if __name__ == "__main__":
    main()
