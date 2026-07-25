# Machine Learning Model

In [[Morse - Master Hub]], the Machine Learning Model acts as **Stage 2 Verification** in our [[Architecture|Cascaded Two-Stage Architecture]].

## 🧬 2D STFT Spectrogram Architecture
Instead of 1D audio spectra, MORSE extracts a **2D Short-Time Fourier Transform (STFT) Spectrogram Image Grid**:
* **Grid Resolution:** $129 \text{ Frequency Bins} \times 15 \text{ Time Frames} = 1,935 \text{ Pixels}$.
* **Temporal Window:** $2,048 \text{ samples}$ ($42.6\text{ms}$ at native 48.0 kHz).
* **Feature Extraction Latency:** $24\mu\text{s}$ (vectorized NumPy FFT).
* **Spatial Pattern Recognition:** Distinguishes **Vertical Impulse Lines (Taps)** from **Horizontal Tonal Beams (Music/Speech)**.

---

## 📊 Master Benchmark (10,214 Spatial Samples)
Evaluated on unseen held-out test splits in `train_2d_spectrogram_model.py`:

| Category | Samples | Precision | Recall | F1-Score | Key Performance Feature |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`left_palm_rest`** | 3,370 | **86%** | **93%** | **0.90** | 93% High-SNR Left Tap Recall |
| **`right_palm_rest`** | 3,657 | **95%** | **100%** 🏆 | **0.97** | 100% Perfect Right Tap Recall (3x Scale Augmented) |
| **`palm_resting`** | 309 | **100%** 🛡️ | **74%** | **0.85** | 100% Precision Against False Wrist/Skin Rustles |
| **`typing`** | 624 | **83%** | **84%** | **0.84** | Multi-Sensor Quartz Hardware Guard Backed |
| **`noise`** | 616 | **86%** | **74%** | **0.79** | High-Pass Spectral Isolation ($> 2,500\text{ Hz}$) |
| **TOTAL** | **10,214** | **90.2% Accuracy** | — | — | **Saved to `model_2d.pkl`** |

---

## 🏆 Head-to-Head Architecture Comparison

| Model Architecture | Overall Accuracy | Left Palm Recall | Right Palm Recall | Training Time |
| :--- | :---: | :---: | :---: | :---: |
| 1D FFT Spectrum (Traditional) | 82.2% | 88.6% | 88.5% | 144.4s |
| **2D STFT Spectrogram (MORSE)** | **84.1% - 90.2% 🏆** | **94.0% 🏆** | **100.0% 🏆** | 185.5s |

---

## ⚖️ 3x Scale Augmentation & Dataset Equilibrium
To solve $30\text{cm}$ unibody aluminum damping for Right Palm Taps without boosting live mic noise floor at runtime:
* **`right_palm_rest` 3x Scale Augmentation:** Generates $1.25\times$ and $0.80\times$ amplitude-scaled copies ($3,657$ samples).
* **`left_palm_rest` 1.5x Scale Augmentation:** Generates $1.15\times$ scale copies ($3,370$ samples).
* **Dual Format Support:** `utils.py` loads both `.npy` and `.wav` audio files seamlessly.

Back to [[Morse - Master Hub]]
