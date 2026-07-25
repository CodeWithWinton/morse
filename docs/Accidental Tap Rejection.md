# Accidental Tap Rejection

How [[Morse - Master Hub]] prevents false activations from table bumps, wristbrushes, and dropped objects.

## Physical Shock Absorption (Desk Bumps)
When someone bumps the table or slides the laptop:
* The **rubber feet** on the bottom of the chassis act as low-pass mechanical shock absorbers.
* Vibration entering through rubber feet has low peak volume and low Crest Factor (< 2.0).
* The [[DSP Engine]] automatically filters out table vibrations before triggering an event.

## Direct Metallic Impacts (Wristwatch Clinks)
Direct metal-on-metal impacts (e.g. a metal wristwatch buckle clinking the aluminum edge, or dropping a pen) produce a real structural shockwave.

## UX Defense: Double-Tap Pattern Window
To make false triggers mathematically zero, Morse relies on **Temporal Multi-Tap Pattern Recognition**:

```
[ Tap #1 Detected ] ─── (Start 350ms Window) ───► [ Tap #2 Detected within 350ms? ]
                                                            │
                                            ┌───────────────┴───────────────┐
                                            │                               │
                                         (YES)                             (NO)
                                            │                               │
                                            ▼                               ▼
                                🎯 TRIGGER ACTION               🔕 Ignore Single Bump
```

* **Single Accidental Bump:** Random, non-repeating event $\rightarrow$ Ignored.
* **Double-Tap (`tap-tap`):** Deliberate human rhythmic input within 350ms $\rightarrow$ Triggers action.

## Multi-Sensor Active Hardware Suppression Guards

To eliminate 100% of false positives while typing or using the mouse, Morse leverages hardware state suppression:

1. **Keyboard Typing Suppressor (`CGEventTap` Guard):**
   * **Human Behavior Invariant:** A user actively typing text on the keyboard will not simultaneously double-tap the palm rest.
   * **Mechanic:** If a physical keypress is detected within a $500\text{ms}$ window prior to an acoustic spike, the candidate audio frame is instantly suppressed ($0\%$ CPU).

2. **Trackpad Motion Suppressor (`MultitouchSupport` Guard):**
   * **Human Behavior Invariant:** A user actively scrolling or dragging on the trackpad is engaged in cursor navigation.
   * **Mechanic:** Active trackpad drag or scroll events suppress acoustic gesture triggers.

3. **Pre-Impact Silent Baseline Guard:**
   * Continuous speech or music has active volume in the $30\text{ms}$ prior to a peak. A true mechanical chassis tap features a dead silent ($0\text{ dB}$) pre-impact baseline.

See [[Future Roadmap]] for multi-tap pattern development milestones.

Back to [[Morse - Master Hub]]
