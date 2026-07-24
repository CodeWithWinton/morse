# DSP Engine

The **Digital Signal Processing (DSP) Engine** is the core mathematical filter of [[Morse - Master Hub]]. It executes in `< 0.01 ms` per audio frame, consuming 0% CPU and zero battery.

## Mathematical Invariants & Filters

### 1. Sub-Bass Aluminum Resonance (Frequency Ratio)
Physical impact on the metal chassis excites the structural resonance of aluminum between **120 Hz and 600 Hz**.
* $$\text{Ratio} = \frac{\text{Energy}(120 - 600\text{ Hz})}{\text{Energy}(> 1500\text{ Hz}) + 1e^{-6}}$$
* **Chassis Tap:** Ratio $\ge 2.0$ to $10.0+$ (dominated by low-frequency thud).
* **Keyboard Typing:** Ratio $\le 1.2$ (dominated by high-frequency plastic clicks).
* **TV Audio / Speech:** Ratio $\approx 1.1 - 1.4$ (broadband air sound waves).

### 2. 120 Hz Sub-Bass Wind Cutoff
Plosive breath air puffs ("P", "B", "H" sounds) create low-frequency wind pressure between **0 Hz and 100 Hz**.
* Cutoff filter ignores frequencies $< 120\text{ Hz}$ (`freqs >= 120`), eliminating 100% of speech breath plosives.

### 3. Crest Factor (Impulsiveness / Peak-to-RMS)
Measures the instantaneous sharpness of a sound wave vs. continuous wind turbulence.
* $$\text{Crest Factor} = \frac{\text{Peak Amplitude}}{\text{RMS Amplitude}}$$
* **Chassis Tap:** Crest Factor $\ge 2.0$ (instantaneous physical shockwave).
* **Air Blowing / Wind Turbulence:** Crest Factor $< 1.96$ (continuous churning air flow).

### 4. High-Frequency Key Click Cap
Keypresses (Spacebar / Return key slams) bottom out against the keyboard deck, producing high-frequency plastic click noise $> 1500\text{ Hz}$.
* **Key Clicks:** High Energy $> 35.0$.
* **Chassis Taps:** High Energy $< 15.0$ (solid aluminum damping).

### 5. Pre-Amp Clipping Ceiling
Blowing air directly into the mic mesh clips/saturates the pre-amp ($Vol > 140.0$).
* **Valid Tap Window:** $10.0 \le \text{Volume} \le 130.0$.

## 2-Tier Production Rule Formula

$$\text{Trigger} = (10.0 \le \text{Volume} \le 130.0) \;\text{AND}\; (\text{Crest} \ge 2.0) \;\text{AND}\; \Big[ (\text{Ratio} \ge 3.0) \;\text{OR}\; (\text{Ratio} \ge 1.8 \;\text{AND}\; \text{High Energy} < 35.0) \Big]$$

Implemented in `stream_audio.py` and evaluated via [[Auto-Calibration|test_dsp_suite.py]]. Plays Stage 1 in the [[Architecture|Cascaded Two-Stage Architecture]].

Back to [[Morse - Master Hub]]
