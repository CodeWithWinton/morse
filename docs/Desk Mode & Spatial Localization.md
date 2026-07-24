# Desk Mode & Spatial Localization

How [[Morse - Master Hub]] expands beyond the laptop chassis to turn the entire physical wooden desk into a spatial gesture controller.

## Table Surface Acoustic Physics
When a user taps the physical desk surface surrounding the laptop:
1. Acoustic shockwaves travel horizontally through the wood/glass/plastic desk surface.
2. The shockwave travels **up through the rubber feet** of the laptop.
3. The internal microphone array picks up the low-frequency **table resonance (80 Hz – 200 Hz)**.

## Time Difference of Arrival (TDOA) Spatial Localization
Modern laptops (MacBook Air/Pro, Dell XPS, ThinkPad) contain **Dual or Triple Microphone Arrays** positioned across the left and right sides of the chassis.

```
[ Left Desk Tap ] ───► Hits Left Mic (0.5ms EARLIER) ───► Hits Right Mic (0.5ms LATER)
                                          │
                                          ▼
                         🎯 SPATIAL DETECTED: LEFT DESK TAP!
```

### Spatial Mapping Matrix

| Physical Location | Acoustic Delay (TDOA) | Dominant Frequencies | Mapped Action |
| :--- | :--- | :--- | :--- |
| **Left Desk Tap** | Left Mic leads by ~0.5ms | 80–200 Hz (Wood) | Previous Track (⏮️) |
| **Right Desk Tap** | Right Mic leads by ~0.5ms | 80–200 Hz (Wood) | Next Track (⏭️) |
| **Chassis Tap** | Dual Mics hit simultaneously | 100–600 Hz (Aluminum) | Mute / Unmute (🔇) |

## Development Timeline
See [[Future Roadmap]] for Phase 2 implementation.

Back to [[Morse - Master Hub]]
