# Acoustic Lessons & Failed Approaches

Engineering case study and empirical post-mortem documenting why naive acoustic approaches fail and how [[Morse - Master Hub]] evolved into a high-precision Cascaded Two-Stage Engine.

## Iteration Evolution & Failed Approaches

| Iteration | Approach | Result | Why It Failed / Engineering Pivot |
| :--- | :--- | :--- | :--- |
| **v1.0** | Single-Tap Pure DSP Threshold | High False Positives (~40%) | Single-tap lacks a temporal dimension; soft thumb taps and accidental palm rest thuds physically overlap in 1D audio amplitude. **Pivot:** Transitioned to Double-Tap pattern matcher ($150\text{ms} - 650\text{ms}$ window). |
| **v2.0** | Truncated 256-Sample ML Classifier | 66.4% Accuracy | Short $5.8\text{ms}$ window truncated the tail end of structural aluminum resonance decay. **Pivot:** Upgraded recording buffer to rolling $2048\text{-sample}$ ($46.4\text{ms}$) windows. |
| **v3.0** | 12 Hand-Crafted Acoustic Features | 78.9% Accuracy | Compressing 2048 audio samples into 12 summary numbers (mean, max, ZCR, ratios) lost high-resolution harmonic spectral shape. **Pivot:** Switched to raw 1025-bin normalized FFT magnitude spectrum. |
| **v4.0 (Current)** | 2048-Sample Raw Spectrogram + Cascaded Two-Stage Engine | 88% ML / 98.5%+ Real-World Pipeline | Full $46.4\text{ms}$ acoustic resolution fed to HistGradientBoosting ML model ($31\mu\text{s}$ latency) combined with Stage 1 Ponytail DSP candidate filter ($0\%$ CPU). |

## Core Engineering Takeaways

1. **The Temporal Dimension Is Non-Negotiable:**
   In 1D acoustic sensing, single impacts cannot reliably separate soft palm rests from soft taps. Adding a temporal constraint (Double-Tap) eliminates 90% of accidental false triggers.

2. **Window Completeness Over Sample Quantity:**
   Truncated audio windows ($5.8\text{ms}$) lose decay dynamics. Capturing pre-impact ambiance, peak transient, and full aluminum resonance decay ($46.4\text{ms}$) is mandatory for spectral separation.

3. **Cascaded Architecture Saves CPU & Battery:**
   Running ML on every raw 10ms audio buffer drains battery and wastes CPU cycles. Using Stage 1 DSP to gate candidate events ($0\%$ CPU) and Stage 2 ML only on candidates achieves $< 0.03\text{ms}$ latency.

Back to [[Morse - Master Hub]]
