# Future Roadmap

Development milestones for [[Morse - Master Hub]].

## Phase 1: Core Acoustic Engine & Calibration (Current)
- [x] Hardware discovery & acoustic pivot ([[Hardware Discovery]]).
- [x] Sub-bass aluminum resonance filter (100–600 Hz) ([[DSP Engine]]).
- [x] Impulse Crest Factor & Transient Decay Rate filters.
- [x] Dataset collection (238 silent room taps + typing + noise).
- [x] [[Auto-Calibration]] wizard (`morse calibrate`).
- [x] [[Architecture|Cascaded Two-Stage Engine]] (DSP Gate + ML Verification).

## Phase 2: Multi-Tap & Spatial Desk Mode
Turn the physical table around the laptop into a multi-zone gesture surface.
* **Multi-Tap Pattern Recognition:** Single Tap, Double Tap, Triple Tap, Hold Tap.
* **Spatial Acoustic Localization:** Using time-difference of arrival (TDOA) across multi-microphone arrays to distinguish taps on the **Left of laptop** vs. **Right of laptop** vs. **Chassis**.
* **Action Integration:** Mute audio, play/pause Spotify, trigger Raycast / Spotlight.

## Phase 3: Desktop UI & Cross-Platform Launch
* **Local Web Dashboard:** Modern dark-mode UI (`http://localhost:5000`) with live audio oscilloscope and visual gesture mapping.
* **macOS Menu Bar Item:** Systray icon for quick toggles.
* **Windows & Linux Support:** [[Open Source Strategy|Cross-platform action adapters]].
* **GitHub Community Launch:** Open-source release on PyPI (`pip install morse-tap`).

Back to [[Morse - Master Hub]]
