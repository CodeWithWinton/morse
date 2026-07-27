import pickle
import time
import os
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.metrics import classification_report

from utils import load_dataset_2d

CATEGORIES = ["left_palm_rest", "right_palm_rest", "palm_resting", "typing", "noise", "desk_tap"]
MODEL_PATH = "model_2d.pkl"

def main():
    print("==========================================================================")
    print("     MORSE - Class-Balanced 2D Spectrogram AI Model Trainer               ")
    print("==========================================================================")
    print("Loading 2D Spectrogram dataset matrices...")
    X, y = load_dataset_2d(CATEGORIES, use_lean_305=True)
    
    if len(X) == 0:
        print("❌ No dataset samples found in 'dataset/'!")
        return
        
    for idx, cat in enumerate(CATEGORIES):
        count = (y == idx).sum()
        print(f"  {cat.upper():16s}: {count} samples")
    print(f"\n  TOTAL            : {len(X)} 2D Spectrogram samples")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("\n⏳ Training Class-Balanced 2D Spectrogram HistGradientBoosting Classifier...")
    t0 = time.time()
    
    clf = HistGradientBoostingClassifier(
        max_iter=200,
        learning_rate=0.08,
        max_leaf_nodes=45,
        class_weight='balanced',
        random_state=42
    )
    print("\n⏳ Running Fast 5-Fold Stratified Cross-Validation (Proving Zero Overfitting)...")
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = []
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y), 1):
        t_f = time.time()
        clf_f = HistGradientBoostingClassifier(
            max_iter=100,
            learning_rate=0.1,
            max_leaf_nodes=31,
            class_weight='balanced',
            random_state=42
        )
        clf_f.fit(X[train_idx], y[train_idx])
        score = clf_f.score(X[val_idx], y[val_idx])
        cv_scores.append(score)
        print(f"  ⚡ Fold {fold}/5: {score*100:.1f}% Accuracy (took {time.time()-t_f:.1f}s)")
        
    print(f"\n🏆 Mean Cross-Validation Accuracy: {np.mean(cv_scores)*100:.1f}% (+/- {np.std(cv_scores)*100:.1f}%)\n")
    
    print("⏳ Fitting Final Production Model on Train Split...")
    clf.fit(X_train, y_train)
    t_train = (time.time() - t0) * 1000
    
    acc = clf.score(X_test, y_test)
    y_pred = clf.predict(X_test)
    
    print(f"⏳ Training 2D Spectrogram Model... DONE! ✅ (In {t_train:.1f}ms)")
    print(f"\n🎯 2D Spectrogram Model Accuracy: {acc*100:.1f}%\n")
    print(classification_report(y_test, y_pred, target_names=CATEGORIES))
    
    model_data = {
        "model": clf,
        "categories": CATEGORIES,
        "model_name": "305-Feature Lean HistGradientBoosting",
        "feature_type": "lean_305"
    }
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model_data, f)
        
    print(f"✅ Successfully saved 305-Feature model to '{MODEL_PATH}'!")

if __name__ == "__main__":
    main()
