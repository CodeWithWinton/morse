# Morse (`-- --- .-. ... .`)

**Concept:** Turn any laptop's chassis into a gesture-sensitive surface using the internal microphone as a Software-Defined Virtual Accelerometer.

## Core Pillars
* [[Core Technology]] — Acoustic Tap Detection via DSP signal processing.
* [[Hardware Discovery]] — Why we pivoted from the accelerometer to the microphone.
* [[DSP Engine]] — The FFT frequency analysis pipeline that powers tap detection.
* [[Accidental Tap Rejection]] — Rubber feet dampening & double-tap UX pattern protection.
* [[Desk Mode & Spatial Localization]] — TDOA multi-mic array for left vs. right desk taps.
* [[Machine Learning Model]] — Role of ML in the Cascaded Two-Stage Architecture.
* [[Acoustic Lessons & Failed Approaches]] — Empirical post-mortem of failed iterations & architectural evolution.
* [[Auto-Calibration]] — The `morse calibrate` wizard for universal laptop support.
* [[Architecture]] — Modular codebase design and Cascaded Dual-Engine.
* [[Open Source Strategy]] — Cross-platform, zero-dependency, FOSS principles.
* [[Future Roadmap]] — Desk Mode, Spatial Detection, and Windows Port.

## Why This Matters
Tapping the aluminum body of a laptop creates a distinct low-frequency structural resonance (100–400 Hz) that travels through the metal frame to the internal microphone. By analyzing this acoustic signature using [[DSP Engine|Digital Signal Processing]], Morse can distinguish a physical chassis tap from keyboard typing, TV audio, speech, and ambient room noise — all without any external hardware, cloud APIs, or paid subscriptions.

## Daily Logs
* [[2026-07-20]] — Project kickoff, accelerometer investigation.
* [[2026-07-24]] — Acoustic pivot, DSP calibration, acid tests, dataset collection.
