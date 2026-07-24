# Machine Learning Model

In [[Morse - Master Hub]], the Machine Learning Model acts as **Stage 2 Verification** in our [[Architecture|Cascaded Two-Stage Architecture]].

## Role in Cascaded Architecture
* **Stage 1 ([[DSP Engine]]):** Discards 90% of quiet room audio in < 0.01 ms with 0% CPU load.
* **Stage 2 (ML Model):** Wakes up *only* when Stage 1 detects a candidate tap impulse, verifying raw spectral features in $45\mu\text{s}$ with 93.6% accuracy and 100% tap recall.

## Model Benchmarks (4-Class AI Benchmark)
Evaluated in `compare_models.py` across 3,507 pristine $46.4\text{ms}$ audio samples (`TAP`, `TYPING`, `PALM_REST`, `NOISE`):

| Model Architecture | 80/20 Accuracy | 5-Fold CV F1 Score | F1 Score | Inference Latency |
| :--- | :--- | :--- | :--- | :--- |
| 🏆 **HistGradientBoosting** | **87.7%** | **84.3% ± 0.7%** | **86.9%** | **$70.91\mu\text{s}$ ($0.07\text{ ms}$)** |
| **Random Forest (100 trees)** | 79.6% | 73.4% ± 1.3% | 75.1% | $14.01\mu\text{s}$ ($0.01\text{ ms}$) |
| **Extra Trees (100 trees)** | 78.3% | 73.0% ± 1.1% | 74.2% | $15.30\mu\text{s}$ ($0.01\text{ ms}$) |

### Classification Performance (`HistGradientBoosting`)
* **Chassis Tap Recall:** **`98% (0.98)`** — Zero missed taps!
* **Chassis Tap Precision:** **`90%`** — High precision against accidental noise.
* **Palm Rest Protection:** **`81% Precision`** — Blocks palm drops while typing (`[✋ ML Blocked: PALM_REST]`).
* **Typing Precision:** **`86%`** — Rejects keyboard keypresses cleanly.

## Feature Extraction (Raw 1025-Bin Spectrogram)
Extracted from a rolling $2048\text{-sample}$ ($46.4\text{ms}$) window:
1. `max_amplitude` (Peak transient amplitude)
2. `crest_factor` (Peak / RMS impulsiveness)
3. `fft_normalized_spectrum` (Full 1025-bin normalized FFT magnitude spectrum)

## Dataset & Training
* Pristine dataset stored in `dataset/` (2,055 Chassis Taps, 473 Typing, 460 Noise).
* Evaluated using 80/20 Stratified Train/Test split and 5-Fold Stratified Cross-Validation.

Back to [[Morse - Master Hub]]
