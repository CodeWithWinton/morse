# Morse (`-- --- .-. ... .`)

**Concept:** Turn any laptop's unibody chassis into a spatial gesture-sensitive surface using the internal microphone as a Software-Defined Virtual Accelerometer.

## Core Pillars
* [[Core Technology]] — Acoustic Tap Detection via DSP signal processing.
* [[Hardware Discovery]] — Hardware mic array analysis (MacBook Air top-left MEMS cluster).
* [[DSP Engine]] — High-Pass Differential Energy Isolation ($> 2,500\text{ Hz}$) and Pre-Impact Baseline Surge Ratio.
* [[Accidental Tap Rejection]] — Quartz `CGEventTap` Multi-Sensor Guards & 100ms Rebound Decay Echo Debounce.
* [[Desk Mode & Spatial Localization]] — Spatial Unibody Palm Rest Localization (`[LEFT]` vs `[RIGHT]`).
* [[Machine Learning Model]] — 3,730-D Spatial Acoustic Feature Space (13,127 HDF5 samples, 98.8% CV, 91.3% zero-leakage test accuracy).
* [[Acoustic Lessons & Failed Approaches]] — Empirical post-mortem of VPIO CoreAudio lock, 1D FFT vs 2D STFT STFT benchmark, and Audio Ducking.
* [[Auto-Calibration]] — Dynamic distance-aware volume floors & scale-augmented volume invariance.
* [[Architecture]] — Multi-Sensor Cascaded Two-Stage Architecture.
* [[Open Source Strategy]] — Cross-platform, zero-dependency, FOSS principles.
* [[Future Roadmap]] — 50+ Laptop Model Data Expansion, IEEE/ACM Research Paper, Product Hunt / Hacker News launch, and Native `MORSE.app` Menu Bar Tray.

## Why This Matters
Tapping the aluminum body of a laptop creates a distinct structural resonance ($120\text{ Hz} - 600\text{ Hz}$) and high-frequency metal ping ($> 2,500\text{ Hz}$) that travels through the frame to the internal microphone. By analyzing this 3,730-D STFT Spectrogram signature, Morse distinguishes physical chassis taps from keyboard typing, trackpad scrolling, speaker music, speech, and ambient room noise — all at 0.3ms latency (<0.3% CPU) without cloud APIs.

## Daily Logs
* [[2026-07-20]] — Project kickoff, accelerometer investigation.
* [[2026-07-24]] — Acoustic pivot, DSP calibration, acid tests, dataset collection.
* [[2026-07-26]] — Native 48.0 kHz upgrade, Quartz CGEventTap guards, 2D STFT Spectrogram AI model (10,214 samples, 100% Right Recall), spatial side tracking (`[LEFT]` vs `[RIGHT]`), and head-to-head empirical benchmarking.
* [[2026-07-29]] — 13,127 HDF5 sample dataset upgrade across MacBook Air and MacBook Neo, 3,730-D feature matrix, and 91.27% zero-leakage unseen test set benchmark.

