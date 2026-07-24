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

See [[Future Roadmap]] for multi-tap pattern development milestones.

Back to [[Morse - Master Hub]]
