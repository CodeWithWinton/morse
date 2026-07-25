import pickle
import time
import os
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

from utils import load_dataset_2d

CATEGORIES = ["tap", "typing", "noise"]
MODEL_PATH = "model_2d.pkl"

def main():
    print("==========================================================================")
    print("     MORSE - Fast 2D Spectrogram AI Model Trainer                         ")
    print("==========================================================================")
    print("Loading 2D Spectrogram dataset matrices...")
    X, y = load_dataset_2d(CATEGORIES)
    
    if len(X) == 0:
        print("❌ No dataset samples found in 'dataset/'!")
        return
        
    for idx, cat in enumerate(CATEGORIES):
        count = (y == idx).sum()
        print(f"  {cat.upper():12s}: {count} samples")
    print(f"\n  TOTAL        : {len(X)} 2D Spectrogram samples")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("\n⏳ Training 2D Spectrogram HistGradientBoosting Classifier...")
    t0 = time.time()
    
    clf = HistGradientBoostingClassifier(
        max_iter=150,
        learning_rate=0.08,
        max_leaf_nodes=31,
        random_state=42
    )
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
        "model_name": "2D Spectrogram HistGradientBoosting",
        "feature_type": "2d_spectrogram"
    }
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model_data, f)
        
    print(f"✅ Successfully saved 2D Spectrogram model to '{MODEL_PATH}'!")

if __name__ == "__main__":
    main()
