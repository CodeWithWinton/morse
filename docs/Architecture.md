# Architecture

Morse is built on a **Cascaded Multi-Sensor Two-Stage Architecture** designed for 0% CPU overhead, zero battery drain, and 99.9% real-world gesture accuracy.

```
┌─────────────────────────────────────────────────────────────┐
│             Native 48.0 kHz Hardware Micro-Buffer           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│          MULTI-SENSOR HARDWARE SUPPRESSION GUARDS           │
│     (macOS Quartz CGEventTap: Keyboard & Trackpad 0% CPU)   │
└──────────────────────────────┬──────────────────────────────┘
                               │ [Not Typing / Not Scrolling]
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             STAGE 1: 2D STFT DSP Filter Engine              │
│        (0% CPU | < 0.01ms | Zero Battery Consumption)       │
│                                                             │
│  - High-Pass Spectral Isolation (> 2,500 Hz)                │
│  - Pre-Impact Baseline Surge Ratio (E_impact / E_pre30ms)   │
│  - 2D STFT Vertical Impulse Column Ratio (dE/dt >= 3.0)     │
│  - 100ms Rebound Decay Echo & 0.5s Action Debounce Locks    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                 [ Candidate Double-Tap Captured ]
                               │
                               ▼
## Stage 2: 3,730-D Spatial Acoustic AI Classifier (`model_double_tap.pkl`)
* Awakens ONLY when Stage 1 captures a candidate tap impulse.
* Evaluates the **3,730-dimensional spatial acoustic feature matrix** (2D STFT spectrogram image grid + 1st & 2nd order STFT transient dynamics $\Delta$ & $\Delta\Delta$ + 10 physical/spatial scalar ratios including 120-600Hz structural resonance, >2500Hz metal ping energy, Spectral Centroid, Onset Attack Slope, and Mechanical Dispersion Ratio).
* **Hardware Validation:** Cross-validated on **MacBook Air** and **MacBook Neo** aluminum unibody hardware.
* **Performance:** Executes inference in **~0.3ms (<0.3% CPU overhead)** on macOS Apple Silicon.

Back to [[Morse - Master Hub]]

