# Morse (`-- --- .-. ... .`)

**Concept:** Turn any laptop's unibody chassis into a spatial gesture-sensitive surface using the internal microphone as a Software-Defined Virtual Accelerometer.

## Core Pillars
* [[Core Technology]] — Acoustic Tap Detection via DSP signal processing.
* [[Hardware Discovery]] — Hardware mic array analysis (MacBook Air top-left MEMS cluster).
* [[DSP Engine]] — High-Pass Differential Energy Isolation ($> 2,500\text{ Hz}$) and Pre-Impact Baseline Surge Ratio.
* [[Accidental Tap Rejection]] — Quartz `CGEventTap` Multi-Sensor Guards & 100ms Rebound Decay Echo Debounce.
* [[Desk Mode & Spatial Localization]] — Spatial Unibody Palm Rest Localization (`[LEFT]` vs `[RIGHT]`).
* [[Machine Learning Model]] — 2D STFT Spectrogram AI Model ($129\times15$, 10,214 balanced samples, 100% Right Recall).
* [[Acoustic Lessons & Failed Approaches]] — Empirical post-mortem of VPIO CoreAudio lock, 1D FFT vs 2D STFT STFT benchmark, and Audio Ducking.
* [[Auto-Calibration]] — Dynamic distance-aware volume floors & scale-augmented volume invariance.
* [[Architecture]] — Multi-Sensor Cascaded Two-Stage Architecture.
* [[Open Source Strategy]] — Cross-platform, zero-dependency, FOSS principles.
* [[Future Roadmap]] — MORSE Radial FX, Mel-Filterbank Scaling, and Native `MORSE.app` Menu Bar Tray.

## Why This Matters
Tapping the aluminum body of a laptop creates a distinct structural resonance ($120\text{ Hz} - 600\text{ Hz}$) and high-frequency metal ping ($> 2,500\text{ Hz}$) that travels through the frame to the internal microphone. By analyzing this 2D STFT Spectrogram signature, Morse distinguishes physical chassis taps from keyboard typing, trackpad scrolling, speaker music, speech, and ambient room noise — all at 0.0% CPU without cloud APIs.

## Daily Logs
* [[2026-07-20]] — Project kickoff, accelerometer investigation.
* [[2026-07-24]] — Acoustic pivot, DSP calibration, acid tests, dataset collection.
* [[2026-07-26]] — Native 48.0 kHz upgrade, Quartz CGEventTap guards, 2D STFT Spectrogram AI model (10,214 samples, 100% Right Recall), spatial side tracking (`[LEFT]` vs `[RIGHT]`), and head-to-head empirical benchmarking.
