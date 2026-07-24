# Machine Learning Model

In [[Morse - Master Hub]], the Machine Learning Model acts as **Stage 2 Verification** in our [[Architecture|Cascaded Two-Stage Architecture]].

## Role in Cascaded Architecture
* **Stage 1 ([[DSP Engine]]):** Discards 99.9% of quiet room audio in 0.01 ms with zero CPU load.
* **Stage 2 (ML Model):** Wakes up *only* when Stage 1 detects a candidate tap impulse, verifying non-linear feature boundaries with > 85% confidence.

## Model Benchmarks
Evaluated in `compare_models.py` across multiple model architectures:

| Model Architecture | Accuracy | Inference Latency | Suitability |
| :--- | :--- | :--- | :--- |
| **Random Forest (100 trees)** | **93.0%** | ~8 μs | **Winner (Best Overall)** |
| **Extra Trees** | 91.5% | ~6 μs | High speed alternative |
| **XGBoost** | 92.2% | ~12 μs | High precision on noisy data |
| **SVM (RBF Kernel)** | 88.4% | ~15 μs | Good for small sample size |

## Feature Vector
Extracted from a 100ms peak transient window:
1. `max_amplitude` (Peak volume spike)
2. `mean_amplitude` (RMS energy)
3. `std_amplitude` (Signal variance)
4. `zero_crossing_rate` (Oscillation speed)
5. `frequency_ratio` (100–600Hz vs > 1500Hz)
6. `crest_factor` (Peak / RMS impulsiveness)
7. `spectral_centroid` (Center mass of spectrum)

## Dataset & Training
* Dataset stored in `dataset/` (238 silent room taps + typing + noise).
* Synthetic Data Augmentation: Tap signals mixed with 50% typing/noise to simulate overlapping ambient sounds.

Back to [[Morse - Master Hub]]
