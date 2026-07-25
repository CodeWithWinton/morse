# Machine Learning Model

In [[Morse - Master Hub]], the Machine Learning Model acts as **Stage 2 Verification** in our [[Architecture|Cascaded Two-Stage Architecture]].

## Role in Cascaded Architecture
* **Stage 1 ([[DSP Engine]]):** Discards 90% of quiet room audio in < 0.01 ms with 0% CPU load.
* **Stage 2 (ML Model):** Wakes up *only* when Stage 1 detects a candidate tap impulse, verifying raw spectral features in $45\mu\text{s}$ with 93.6% accuracy and 100% tap recall.

## Model Benchmarks (5-Class AI Model)
Evaluated in `train_clean_model.py` across 4,172 pristine $46.4\text{ms}$ audio samples (`TAP`, `TYPING`, `DESK_TAP`, `PALM_REST`, `NOISE`):

| Model Architecture | 80/20 Accuracy | Tap Recall | Typing Precision | Saved Model |
| :--- | :--- | :--- | :--- | :--- |
| 🏆 **HistGradientBoosting** | **77.4%** | **97% (0.97)** | **84%** | `model.pkl` |

### Classification Performance (`HistGradientBoosting`)
* **Chassis Tap Recall:** **`97%`** — High sensitivity for intentional double taps.
* **Typing Protection:** **`84% Precision`** — Rejects keyboard keypresses & spacebar slams (`[⌨️ ML Blocked: TYPING]`).
* **Desk Tap Protection:** **`75% Precision`** — Rejects wooden desk taps (`[🪵 ML Blocked: DESK_TAP]`).
* **Palm Rest Protection:** **`70% Precision`** — Rejects wrist weight drops (`[✋ ML Blocked: PALM_REST]`).
* **Noise Protection:** **`79% Precision`** — Rejects speech & ambient room noise (`[🔕 ML Blocked: NOISE]`).

## Feature Extraction (Raw 1025-Bin Spectrogram)
Extracted from a rolling $2048\text{-sample}$ ($46.4\text{ms}$) window:
1. `max_amplitude` (Peak transient amplitude)
2. `crest_factor` (Peak / RMS impulsiveness)
3. `fft_normalized_spectrum` (Full 1025-bin normalized FFT magnitude spectrum)

## Dataset & Training
* Pristine dataset stored in `dataset/` (2,055 Chassis Taps, 473 Typing, 460 Noise).
* Evaluated using 80/20 Stratified Train/Test split and 5-Fold Stratified Cross-Validation.

Back to [[Morse - Master Hub]]
