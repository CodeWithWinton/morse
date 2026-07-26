import time
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

from utils import load_dataset, load_dataset_2d

CATEGORIES = ["left_palm_rest", "right_palm_rest", "palm_resting", "typing", "noise", "desk_tap"]

def main():
    print("==========================================================================")
    print("     MORSE Benchmark: 1D FFT Spectrum vs 2D STFT Spectrogram              ")
    print("==========================================================================")
    
    # 1D FFT Data
    print("\n📊 [1/2] Loading 1D FFT Magnitude Spectrum Dataset...")
    X_1d, y_1d = load_dataset(CATEGORIES)
    X_1d_train, X_1d_test, y_1d_train, y_1d_test = train_test_split(X_1d, y_1d, test_size=0.2, random_state=42, stratify=y_1d)
    
    print("⏳ Training 1D FFT Classifier...")
    t0 = time.time()
    clf_1d = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, max_leaf_nodes=45, class_weight='balanced', random_state=42)
    clf_1d.fit(X_1d_train, y_1d_train)
    t_1d = (time.time() - t0) * 1000
    acc_1d = clf_1d.score(X_1d_test, y_1d_test)
    
    # 2D Spectrogram Data
    print("\n📊 [2/2] Loading 2D STFT Spectrogram Matrix Dataset...")
    X_2d, y_2d = load_dataset_2d(CATEGORIES)
    X_2d_train, X_2d_test, y_2d_train, y_2d_test = train_test_split(X_2d, y_2d, test_size=0.2, random_state=42, stratify=y_2d)
    
    print("⏳ Training 2D STFT Spectrogram Classifier...")
    t0 = time.time()
    clf_2d = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.08, max_leaf_nodes=45, class_weight='balanced', random_state=42)
    clf_2d.fit(X_2d_train, y_2d_train)
    t_2d = (time.time() - t0) * 1000
    acc_2d = clf_2d.score(X_2d_test, y_2d_test)
    
    # Compare Recall for Left & Right Palm Taps
    y_1d_pred = clf_1d.predict(X_1d_test)
    y_2d_pred = clf_2d.predict(X_2d_test)
    
    rep_1d = classification_report(y_1d_test, y_1d_pred, target_names=CATEGORIES, output_dict=True)
    rep_2d = classification_report(y_2d_test, y_2d_pred, target_names=CATEGORIES, output_dict=True)
    
    print("\n==========================================================================")
    print("                      HEAD-TO-HEAD BENCHMARK RESULTS                      ")
    print("==========================================================================")
    print(f"| Architecture           | Overall Accuracy | Left Palm Recall | Right Palm Recall | Training Time |")
    print(f"|------------------------|------------------|------------------|-------------------|---------------|")
    print(f"| 1D FFT Spectrum        | {acc_1d*100:.1f}%             | {rep_1d['left_palm_rest']['recall']*100:.1f}%            | {rep_1d['right_palm_rest']['recall']*100:.1f}%             | {t_1d/1000:.1f}s          |")
    print(f"| 2D STFT Spectrogram    | {acc_2d*100:.1f}%             | {rep_2d['left_palm_rest']['recall']*100:.1f}%            | {rep_2d['right_palm_rest']['recall']*100:.1f}%             | {t_2d/1000:.1f}s          |")
    print("==========================================================================")

if __name__ == "__main__":
    main()
