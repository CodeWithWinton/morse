# Machine Learning Model

In [[Morse - Master Hub]], the Machine Learning Model acts as **Stage 2 Verification** in our [[Architecture|Cascaded Two-Stage Architecture]].

## Role in Cascaded Architecture
* **Stage 1 ([[DSP Engine]]):** Discards 90% of quiet room audio in < 0.01 ms with 0% CPU load.
* **Stage 2 (ML Model):** Wakes up *only* when Stage 1 detects a candidate tap impulse, verifying raw spectral features in $45\mu\text{s}$ with 93.6% accuracy and 100% tap recall.

## Model Benchmarks (3-Class AI Benchmark)
Evaluated in `compare_models.py` across 2,988 pristine $46.4\text{ms}$ audio samples (`TAP`, `TYPING`, `NOISE`):

| Model Architecture | Accuracy | Precision | Recall | F1 Score | Inference Latency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 🏆 **HistGradientBoosting** | **93.6%** | **93.6%** | **93.6%** | **93.4%** | **$45.86\mu\text{s}$ ($0.04\text{ ms}$)** |
| **Random Forest (200 trees)** | 88.8% | 89.7% | 88.8% | 88.0% | $30.29\mu\text{s}$ ($0.03\text{ ms}$) |
| **Extra Trees (200 trees)** | 88.1% | 89.0% | 88.1% | 87.2% | $26.23\mu\text{s}$ ($0.03\text{ ms}$) |
| **SVM (RBF Kernel)** | 86.5% | 89.5% | 86.5% | 87.2% | $399.80\mu\text{s}$ ($0.40\text{ ms}$) |
| **K-Nearest Neighbors** | 84.9% | 85.5% | 84.9% | 83.4% | $206.68\mu\text{s}$ ($0.20\text{ ms}$) |

### Classification Performance (`HistGradientBoosting`)
* **Chassis Tap Recall:** **`100% (1.00)`** — Zero missed taps!
* **Chassis Tap Precision:** **`94%`** — High precision against accidental noise.
* **Typing Precision:** **`96%`** — Rejects keyboard keypresses cleanly.

## Feature Extraction (Raw 1025-Bin Spectrogram)
Extracted from a rolling $2048\text{-sample}$ ($46.4\text{ms}$) window:
1. `max_amplitude` (Peak transient amplitude)
2. `crest_factor` (Peak / RMS impulsiveness)
3. `fft_normalized_spectrum` (Full 1025-bin normalized FFT magnitude spectrum)

## Dataset & Training
* Pristine dataset stored in `dataset/` (2,055 Chassis Taps, 473 Typing, 460 Noise).
* Evaluated using 80/20 Stratified Train/Test split and 5-Fold Stratified Cross-Validation.

Back to [[Morse - Master Hub]]
