# Machine Learning Model

In [[Morse - Master Hub]], the Machine Learning Model acts as **Stage 2 Verification** in our [[Architecture|Cascaded Two-Stage Architecture]].

## 🧬 2D STFT Spectrogram Architecture
Instead of 1D audio spectra, MORSE extracts a **2D Short-Time Fourier Transform (STFT) Spectrogram Image Grid**:
* **Grid Resolution:** $129 \text{ Frequency Bins} \times 15 \text{ Time Frames} = 1,935 \text{ Pixels}$.
* **Temporal Window:** $2,048 \text{ samples}$ ($42.6\text{ms}$ at native 48.0 kHz).
* **Feature Extraction Latency:** $24\mu\text{s}$ (vectorized NumPy FFT).
* **Spatial Pattern Recognition:** Distinguishes **Vertical Impulse Lines (Taps)** from **Horizontal Tonal Beams (Music/Speech)**.

---

## 📊 Master Benchmark (13,127 HDF5 Ground-Truth Samples)

Evaluated on `morse_dataset.h5` in `train_double_tap_model.py`:

| Category | Raw Samples | Precision | Recall | F1-Score | Performance Feature |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`double_left_palm`** | 3,000 | **0.88** | **0.90** | **0.89** | High-SNR Left Tap Detection |
| **`double_right_palm`** | 3,000 | **0.87** | **0.83** | **0.85** | Aluminum Chassis Damped Right Tap Detection |
| **`noise_and_typing`** | 7,127 | **0.95** 🛡️ | **0.96** 🛡️ | **0.95** | High Immunity to Background Reels / TV / Typing Noise |
| **TOTAL** | **13,127** | **98.8% CV** | **91.3% Unseen Test** | — | **Saved to `model_double_tap.pkl`** |

---

## 🏆 Key Metrics Summary
* **5-Fold Cross-Validation Accuracy:** **98.8%** (with 0.8x–1.2x amplitude variations)
* **Zero-Leakage Unseen Test Accuracy:** **91.27%** (raw sample split *before* feature extraction/augmentation)
* **Feature Dimension:** **3,730-D Spatial Feature Space**
* **Inference Latency:** **~0.3ms (<0.3% CPU load)**

Back to [[Morse - Master Hub]]

