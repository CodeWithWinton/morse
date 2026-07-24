# DSP Engine

The **Digital Signal Processing (DSP) Engine** is the core mathematical filter of [[Morse - Master Hub]]. It executes in `< 0.01 ms` per audio frame, consuming 0% CPU and zero battery.

## Mathematical Invariants

### 1. Sub-Bass Aluminum Resonance (Frequency Ratio)
Physical impact on the metal chassis excites the structural resonance of aluminum between **100 Hz and 600 Hz**.
* $$\text{Ratio} = \frac{\text{Energy}(50 - 600\text{ Hz})}{\text{Energy}(> 1500\text{ Hz}) + 1e^{-6}}$$
* **Chassis Tap:** Ratio $\ge 3.0$ (dominated by low-frequency thud).
* **Keyboard Typing:** Ratio $\le 0.8$ (dominated by high-frequency plastic clicks).
* **TV Audio / Speech:** Ratio $\approx 1.1$ (broadband air sound waves).

### 2. Crest Factor (Impulsiveness / Peak-to-RMS)
Measures the instantaneous sharpness of a sound wave.
* $$\text{Crest Factor} = \frac{\text{Peak Amplitude}}{\text{RMS Amplitude}}$$
* **Chassis Tap:** Crest Factor $\ge 2.3$ (instantaneous physical shockwave).
* **TV Speech / Room Noise:** Crest Factor $< 2.0$ (smooth continuous wave).

### 3. Transient Post-Peak Decay Ratio
Measures how fast energy dampens after the peak.
* $$\text{Decay Ratio} = \frac{\text{Energy after 10ms post-peak}}{\text{Energy at peak spike}}$$
* **Chassis Tap:** Decay Ratio $< 0.30$ (metal dampens vibration instantly).
* **Loud TV Audio / Room Reverberation:** Decay Ratio $> 0.70$ (sound lingers in the air).

## Implementation
Implemented in `dsp_filter.py` and evaluated offline via [[Auto-Calibration|test_dsp_suite.py]]. Plays Stage 1 in the [[Architecture|Cascaded Two-Stage Architecture]].

Back to [[Morse - Master Hub]]
