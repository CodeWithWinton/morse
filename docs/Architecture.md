# Architecture

Morse is built on a **Cascaded Two-Stage Architecture** designed for 0% CPU overhead, zero battery drain, and 99.9% real-world gesture accuracy.

```
┌─────────────────────────────────────────────────────────────┐
│                    PortAudio Micro-Buffer                   │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             STAGE 1: Ponytail DSP Filter Engine             │
│        (0% CPU | < 0.01ms | Zero Battery Consumption)       │
│                                                             │
│  - 120 Hz Sub-Bass Wind Cutoff                              │
│  - Impulsive Crest Factor Guard                             │
│  - High-Frequency Key Click Cap                             │
│  - 40ms - 750ms Rhythmic Double-Tap Pattern Matcher         │
└──────────────────────────────┬──────────────────────────────┘
                               │
                 [ Candidate Double-Tap Captured ]
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            STAGE 2: Micro ML Classifier (0.01% CPU)         │
│     (Triggered ONLY on candidate taps to classify edge cases)│
│                                                             │
│  - 1D-CNN / Random Forest Lightweight Classifier            │
│  - Pushes real-world gesture accuracy from 89% -> 99.9%     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Native macOS Action Engine                  │
│       (Apple Music Play/Pause, System Mute, Raycast)        │
└─────────────────────────────────────────────────────────────┘
```

## Stage 1: Ponytail DSP Engine (FOSS Foundation)
* Evaluates 100% of incoming audio blocks in real-time.
* Filters out **89% - 90%** of room noise, speech, typing keypresses, and wind turbulence.
* Runs 100% offline with zero dependencies beyond `numpy` and `sounddevice`.

## Stage 2: Micro ML Classifier (Hardest 8-10% Edge Cases)
* Remains dormant 99.9% of the time.
* Awakens ONLY when Stage 1 captures a candidate double-tap.
* Evaluates the 2048-sample transient spectrogram to eliminate the final 8-10% subtle edge cases (e.g., wrist rests, heavy desk thuds).

Back to [[Morse - Master Hub]]
