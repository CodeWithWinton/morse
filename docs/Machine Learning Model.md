# Machine Learning Model

In [[Morse - Master Hub]], the Machine Learning Model acts as **Stage 2 Verification** in our [[Architecture|Cascaded Two-Stage Architecture]].

## Role in Cascaded Architecture
* **Stage 1 ([[DSP Engine]]):** Discards 90% of quiet room audio in < 0.01 ms with 0% CPU load.
* **Stage 2 (ML Model):** Wakes up *only* when Stage 1 detects a candidate tap impulse, verifying raw spectral features in $45\mu\text{s}$ with 93.6% accuracy and 100% tap recall.

## Model Benchmarks (3-Class AI Benchmark)
Evaluated in `compare_models.py` across 2,988 pristine $46.4\text{ms}$ audio samples (`TAP`, `TYPING`, `NOISE`):

| Model Architecture | 80/20 Accuracy | 5-Fold CV F1 Score | F1 Score | Inference Latency |
| :--- | :--- | :--- | :--- | :--- |
| 🏆 **HistGradientBoosting** | **93.6%** | **91.5% ± 1.4%** | **93.4%** | **$39.63\mu\text{s}$ ($0.04\text{ ms}$)** |
| **Random Forest (200 trees)** | 88.8% | 86.0% ± 1.2% | 88.0% | $23.85\mu\text{s}$ ($0.02\text{ ms}$) |
| **Extra Trees (200 trees)** | 88.1% | 86.1% ± 1.1% | 87.2% | $26.05\mu\text{s}$ ($0.03\text{ ms}$) |
| **SVM (RBF Kernel)** | 86.5% | 86.2% ± 0.8% | 87.2% | $426.94\mu\text{s}$ ($0.42\text{ ms}$) |
| **K-Nearest Neighbors** | 84.9% | 81.8% ± 1.2% | 83.4% | $49.70\mu\text{s}$ ($0.05\text{ ms}$) |

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
