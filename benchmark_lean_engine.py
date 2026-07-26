import time
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, recall_score, precision_score
from utils import load_dataset_2d, extract_lean_305_features, extract_2d_spectrogram

CATEGORIES = ["left_palm_rest", "right_palm_rest", "palm_resting", "typing", "noise", "desk_tap"]

print("============================================================")
print("  MORSE - 305-Feature Lean Engine vs. Baseline Benchmark")
print("============================================================")

# 1. Feature Extraction Latency Micro-Benchmark
dummy_signal = np.random.randn(2048).astype(np.float32)

t0 = time.perf_counter()
for _ in range(1000):
    _ = extract_2d_spectrogram(dummy_signal)
time_2d = (time.perf_counter() - t0) / 1000 * 1e6 # microseconds

t0 = time.perf_counter()
for _ in range(1000):
    _ = extract_lean_305_features(dummy_signal)
time_lean = (time.perf_counter() - t0) / 1000 * 1e6 # microseconds

print(f"\n⚡ Feature Extraction Latency (1,000 runs):")
print(f"   - Baseline 2D Spectrogram (1,942 features): {time_2d:.2f} µs")
print(f"   - Lean Engine (305 features):             {time_lean:.2f} µs  ({(1 - time_lean/time_2d)*100:.1f}% faster!)")

# 2. Dataset Loading & Model Benchmarking
print("\n📦 Loading Dataset with Lean 305 Features...")
t0 = time.perf_counter()
X, y = load_dataset_2d(CATEGORIES, use_lean_305=True)
load_time = time.perf_counter() - t0
print(f"   - Loaded {len(X)} augmented samples in {load_time:.2f}s")
print(f"   - Feature Matrix Shape: {X.shape}")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

print("\n🧠 Training HistGradientBoostingClassifier on Lean 305 Features...")
clf = HistGradientBoostingClassifier(random_state=42, max_iter=150)
t0 = time.perf_counter()
clf.fit(X_train, y_train)
train_time = time.perf_counter() - t0
print(f"   - Model trained in {train_time:.2f}s")

# 3. Model Inference Micro-Benchmark
t0 = time.perf_counter()
for _ in range(1000):
    _ = clf.predict([X_test[0]])
infer_time = (time.perf_counter() - t0) / 1000 * 1e6

print(f"\n⚡ Model Inference Speed: {infer_time:.2f} µs per sample")
print(f"🚀 Total System Latency (Extraction + ML): {time_lean + infer_time:.2f} µs")

# 4. Accuracy & Recall Breakdown
y_pred = clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print("\n📊 Accuracy & Class Performance Breakdown:")
print(f"   - Overall Accuracy: {acc*100:.2f}%")

target_names = [c for c in CATEGORIES if c in CATEGORIES]
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=target_names[:len(np.unique(y))]))

print("\n✅ Benchmark Complete!")
