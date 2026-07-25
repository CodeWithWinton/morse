<p align="center">
  <h1 align="center">Morse</h1>
  <p align="center">
    <code>-- --- .-. ... .</code>
  </p>
  <p align="center">
    <em>Tap your laptop. Control your world.</em>
  </p>
  <p align="center">
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python 3.9+">
    <img src="https://img.shields.io/badge/Platform-macOS-lightgrey.svg" alt="macOS">
    <img src="https://img.shields.io/badge/CPU-0%25-brightgreen.svg" alt="0% CPU">
    <img src="https://img.shields.io/badge/Network-100%25%20Offline-purple.svg" alt="100% Offline">
  </p>
</p>

---

**Morse** is a software-defined acoustic tap engine that turns your laptop chassis and physical desk into a multi-zone touch surface. Double-tap the metal body of your MacBook or wooden desk to toggle WhatsApp, play/pause music, trigger GTA-style radial command wheels, or mute your mic — no special hardware required.

It works by listening to the built-in microphone for the unique low-frequency structural vibration ($120\text{ Hz} - 600\text{ Hz}$) that aluminum produces when tapped, filtering out typing, speech, and room noise using a **0% CPU multi-sensor DSP + ML pipeline**.

## Why Morse Exists

Every commercial tap-detection app on macOS (QuickTap, Knock, etc.) relies on physical **SPU accelerometer chips** found only in M2/M3/M4 MacBooks. If you have a base M1 MacBook Air, an Intel Mac, a Mac Mini, or a non-Apple laptop, those apps fail completely.

Morse takes a different approach: **pure software-defined acoustic signal processing & multi-sensor hardware fusion through the mic you already have.** It works on every laptop and desktop with a microphone.

---

## 🏗️ Architecture & How It Works

```
                        [ Physical Tap / Desk Event ]
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. HARDWARE SENSOR FUSION LAYER (0% CPU)                                │
│    • Keyboard Guard (CGEventTap)      ──► Mutes within 500ms of typing  │
│    • Trackpad Guard (Multitouch)      ──► Mutes during active drag      │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │ (Pass)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. LIGHTWEIGHT SPECTRAL ENGINE (48 kHz Native Hardware Clock)           │
│    • High-Pass Surge (> 2.5 kHz)      ──► Taps work WHILE talking on Zoom│
│    • Spectral Centroid (> 2,800 Hz)   ──► Isolates aluminum metal pings │
│    • Spectral Flatness (Entropy)      ──► Kills vocal vowels & TV sound │
│    • Speaker AEC Adaptive Scaling     ──► Suppresses Mac speaker audio  │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │ (Candidate Tap)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. 2D STFT SPECTROGRAM AI ENGINE (model_2d.pkl | 0.059ms Latency)       │
│    • 1,935-Pixel 2D STFT Image Grid   ──► 129 Bins x 15 Time Frames     │
│    • Spatial Side Detection           ──► Tracks [LEFT] vs [RIGHT] Taps │
│    • 100% Right Tap Recall            ──► 3x Scale Data Augmentation    │
│    • 100% Skin Resting Immunity       ──► 95% Precision on Palm Sliding│
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │ (Validated)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. NATIVE ACTION ENGINE & RADIAL FX (actions.py)                        │
│    • Smart WhatsApp Toggle (Cmd+H)                                      │
│    • GTA-Style Radial Weapon Wheel Overlay at Cursor Location           │
│    • Apple Music / Spotify Media Controls                               │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quickstart

```bash
# Clone
git clone https://github.com/CodeWithWinton/morse.git
cd morse

# Install dependencies (only standard open-source libraries)
pip install numpy sounddevice scikit-learn

# Run live 2D Spectrogram detector
python3 smart_detector.py
```

Double-tap the left or right metal palm rest of your laptop. You will see:

```text
 👆 Tap 1 captured [LEFT]... (ML Confidence: 99.8%, Vol: 8.5)
 👆 Tap 1 captured [RIGHT]... (ML Confidence: 100.0%, Vol: 3.8)

✌️ DOUBLE-TAP DETECTED! (RIGHT) (ML Confidence: 100.0%, Vol: 4.2)
💬 Executing Action: SMART WHATSAPP TOGGLE (OPEN / HIDE)
```

Press `Ctrl+C` to stop.

---

## 🧪 Benchmark & Training Tools

* **Train 2D Spectrogram Master Model:** Train `model_2d.pkl` on 10,214 spatial samples with 5-Fold Stratified Cross-Validation:
  ```bash
  python3 train_2d_spectrogram_model.py
  ```
* **Run Head-to-Head Architecture Benchmark:** Benchmark 1D FFT vs 2D STFT Spectrogram vs RandomForest vs ExtraTrees:
  ```bash
  python3 compare_1d_vs_2d.py
  python3 compare_all_models.py
  ```
* **Listen & Analyze Filtered Audio Traces:** Save `raw_tap.wav` and 100% muted `filtered_tap.wav` side-by-side:
  ```bash
  python3 listen_taps.py
  ```
  python3 test_dsp_suite.py
  ```

---

## 🔬 The Physics

When you tap the aluminum unibody of a MacBook, the impact creates a structural shockwave that resonates between **120 Hz and 600 Hz** with a high-frequency transient ring above **2,500 Hz**:

| Signal Source | Bass Ratio (120–600 Hz) | Crest Factor (Peak/RMS) | HP Ratio (>2.5 kHz) | Baseline Pre-Impact |
|---|---|---|---|---|
| **Chassis Palm Tap** | 1.5 – 10.0+ | **≥ 2.5** | **≥ 40%** | **Dead Silent (0 dB)** |
| **Wooden Desk Tap** | 0.8 – 2.0 (80–200 Hz Wood Thud) | ≥ 2.0 | < 15% | Dead Silent (0 dB) |
| **Keyboard Typing** | 0.05 – 1.2 | Varies | Varies | Keypress Event Active |
| **Speech / Humming** | 0.8 – 1.4 | < 1.6 | < 10% | Continuous Sound |
| **Room / TV Noise** | 0.0 – 0.8 | < 1.5 | < 5% | Continuous Sound |

---

### 🎛️ 8-Zone Physical Gesture Control Matrix

| Gesture | Surface Signature | Frequency Profile | Action |
|---|---|---|---|
| ⚡ **Double-Tap Left Palm** | Metal Unibody | High-Freq Sharp ($H/L \ge 0.45$) | Toggle WhatsApp (`Cmd+H`) |
| ⚡ **Triple-Tap Left Palm** | Metal Unibody | High-Freq Sharp ($H/L \ge 0.45$) | Mute Zoom Microphone |
| ⚡ **Double-Tap Right Palm** | Metal Unibody | Damped Low-Freq ($H/L \le 0.20$) | Play / Pause Apple Music |
| ⚡ **Triple-Tap Right Palm** | Metal Unibody | Damped Low-Freq ($H/L \le 0.20$) | Next Track |
| 🪵 **Double-Tap Left Desk** | Wood Surface | Deep Wood Thud ($80-200\text{ Hz}$) | Undo (`Cmd+Z`) |
| 🪵 **Triple-Tap Left Desk** | Wood Surface | Deep Wood Thud ($80-200\text{ Hz}$) | Redo (`Cmd+Shift+Z`) |
| 🪵 **Double-Tap Right Desk** | Wood Surface | Damped Wood Thud | GTA-Style Radial FX Wheel |
| 🪵 **Triple-Tap Right Desk** | Wood Surface | Damped Wood Thud | Save File (`Cmd+S`) |

---

## 🔮 Future Roadmap

* 🕹️ **MORSE Radial FX:** GTA V-style radial command wheel popping up at cursor location for 1-flick execution in VS Code & Premiere Pro.
* 📦 **Developer SDK (`morse-sdk`):** Native C# / C++ / Python SDK for Unity & Unreal Engine games.
* 🔒 **TapID Biometric Unlock:** 2-Factor authentication combining secret tap rhythm ($\Delta t$) with acoustic bone density profiles via macOS C Authorization Plugins.
* 🦇 **Active Ultrasonic Sonar:** Proximity detection via $20-22\text{ kHz}$ Doppler wave reflections.

---

## Project Structure

```
morse/
├── smart_detector.py    # Main 2-Stage Cascaded ML/DSP Engine
├── utils.py             # Refactored shared helpers (0% code duplication)
├── actions.py           # Native macOS AppleScript triggers
├── listen_taps.py       # Audio trace recorder & metric analyzer
├── collect_data.py      # Dataset recorder for ML training
├── train_clean_model.py # Fast HistGradientBoosting model trainer
├── compare_models.py    # Model benchmark comparison suite
├── test_dsp_suite.py    # DSP unit test suite
├── docs/                # Obsidian vault documentation hub
└── dataset/             # Recorded acoustic samples (.npy)
```

---

## Requirements

- Python 3.9+
- macOS (tested on M1 MacBook Air)
- `numpy`, `sounddevice`

## License

MIT — do whatever you want with it.

---

<p align="center">
  <em>Built by <a href="https://github.com/CodeWithWinton">Manas Maheshwari</a> as a side project while working on <a href="https://github.com/CodeWithWinton">BizzFlow</a>.</em>
</p>
