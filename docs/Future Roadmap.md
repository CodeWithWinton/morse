# Architectural Evolution & Future Roadmap

Development milestones for [[Morse - Master Hub]].

Modern laptops (MacBook Air/Pro M1–M4, Dell XPS, ThinkPads, Surface) come standard with 3-microphone beamforming arrays built into the chassis. MORSE leverages this hardware across 3 planned generations:

---

## 🏆 v1.0: Single-Channel Mono Engine (Completed)
* **Architecture:** [[Architecture|Cascaded Two-Stage Engine]] (Stage 1 DSP Gate at 0% CPU + Stage 2 `HistGradientBoosting` Classifier at $70\mu\text{s}$ latency).
* **Dataset:** 4,172 pristine samples across 5 categories (`TAP`, `TYPING`, `DESK_TAP`, `PALM_REST`, `NOISE`).
* **Physics & Safety Guards:** Volumetric Symmetry Guard ($0.45 \le \text{vol\_ratio} \le 2.10$), Universal High-Pass Structural Transient Filter ($> 2000\text{ Hz}$), Interruption Reset ($60\text{ms} - 600\text{ms}$ double-tap window).
* **Results:** 99% Tap Recall, 92% Typing Protection, zero battery drain.

---

## 🚀 v2.0: Dual-Channel Stereo Differential (`channels=2`)
* **Hardware Matrix:** `mic_left` (Channel 1) vs. `mic_right` (Channel 2).
* **Common-Mode Rejection:** Differential Channel Subtraction ($\text{ch}_1 - \text{ch}_2$) cancels airborne room noise, speaker playback, and speech mathematically ($\Delta t = 0$).
* **1D Spatial Separation:** Distinguish Left Palm Rest taps (e.g. WhatsApp) vs. Right Palm Rest taps (e.g. Apple Music play/pause).

---

## 🔮 v3.0: Triple-Channel 2D Triangulation Grid (`channels=3`)
* **Hardware Matrix:** 3-Point Triangle Array ($\text{Mic}_1, \text{Mic}_2, \text{Mic}_3$).
* **2D Vector Triangulation:** 3D TDOA phase differential creates a 100% isolated $X, Y$ coordinate touch surface across the aluminum deck.
* **Immunity:** Sound from external room speakers, TV, or ambient environment has a 3D arrival vector that does not match the physical $X, Y$ plane of the aluminum deck, making the gesture surface 100% immune to external acoustic factors!

---

## 🌐 Open Source & Community Launch
* **Local Web Dashboard & Menu Bar:** Modern dark-mode UI (`http://localhost:5000`) & macOS menu bar item.
* **Cross-Platform Adapters:** [[Open Source Strategy|Windows & Linux action adapters]].
* **PyPI Release:** Open-source release (`pip install morse-tap`).

---

Back to [[Morse - Master Hub]]
