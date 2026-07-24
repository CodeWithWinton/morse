# Desk Mode & Spatial Localization

How [[Morse - Master Hub]] expands beyond the laptop chassis to turn the entire physical wooden desk and left/right chassis sides into a spatial gesture controller.

## Table & Chassis Acoustic Physics
When a user taps the physical chassis or desk surface:
1. Acoustic shockwaves travel through aluminum or the surrounding desk surface.
2. Shockwaves hit the **Dual or Triple Microphone Array** (Left Mic & Right Mic).
3. Microsecond Time Difference of Arrival (TDOA) phase delays determine spatial location.

## Time Difference of Arrival (TDOA) Spatial Localization
Modern laptops (MacBook Air/Pro, Dell XPS) contain **Dual or Triple Microphone Arrays** positioned across the left and right sides of the chassis.

```
[ Left Side Tap ] ───► Hits Left Mic (Microseconds EARLIER) ───► Hits Right Mic
                                       │
                                       ▼
                       🎯 SPATIAL DETECTED: LEFT TAP (WhatsApp Toggle)
```

### Spatial Mapping Matrix

| Physical Location | Acoustic Delay (TDOA) | Dominant Frequencies | Mapped Action |
| :--- | :--- | :--- | :--- |
| **Left Chassis Double-Tap** | Left Mic leads phase | 120–600 Hz (Aluminum) | Smart WhatsApp Toggle (Open / Hide `Cmd+H`) 💬 |
| **Right Chassis Double-Tap** | Right Mic leads phase | 120–600 Hz (Aluminum) | Apple Music Play / Pause (🎵) |
| **Left Desk Tap** | Left Mic leads by ~0.5ms | 80–200 Hz (Wood) | Previous Track (⏮️) |
| **Right Desk Tap** | Right Mic leads by ~0.5ms | 80–200 Hz (Wood) | Next Track (⏭️) |

## Smart Window Toggle Actions
Instead of destroying application processes with destructive `Cmd+Q` termination:
* **Focus Check:** Evaluates frontmost application process via macOS System Events.
* **If App is Hidden/Background:** Brings application to frontmost focus (`open -a AppName`).
* **If App is Active/Frontmost:** Instantly hides application (`Cmd+H` equivalent: `set visible of process to false`), restoring immediate user productivity context!

## Development Timeline
See [[Future Roadmap]] for Phase 2 spatial TDOA implementation.

Back to [[Morse - Master Hub]]
