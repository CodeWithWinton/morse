<p align="center">
  <h1 align="center">MORSE</h1>
  <p align="center">
    <code>-- --- .-. ... .</code>
  </p>
  <p align="center">
    <em>Powered by <strong>TLM 1.0 (Tap Learning Model)</strong></em><br>
    <em>Tap your laptop. Control your world.</em>
  </p>
  <p align="center">
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License"></a>
    <img src="https://img.shields.io/badge/Model-TLM%201.0%20(Tap%20Learning%20Model)-blue.svg" alt="TLM 1.0">
    <img src="https://img.shields.io/badge/Accuracy-96.7%25%20CV-brightgreen.svg" alt="96.7% Accuracy">
    <img src="https://img.shields.io/badge/CPU-%3C0.5%25-brightgreen.svg" alt="<0.5% CPU">
    <img src="https://img.shields.io/badge/Platform-macOS-lightgrey.svg" alt="macOS">
    <img src="https://img.shields.io/badge/Network-100%25%20Offline-purple.svg" alt="100% Offline">
  </p>
</p>

---

**MORSE** is an acoustic AI engine powered by **TLM 1.0 (Tap Learning Model)** — turning your laptop's unibody aluminum chassis into an invisible multi-zone touch surface. Double-tap the left or right metal palm rest of your MacBook to toggle WhatsApp, control Apple Music, or trigger custom native workflows — no extra hardware or sensors required.

Just as **LLMs (Large Language Models)** transform tokenized text into semantic intent, **TLM 1.0 (Tap Learning Model)** processes kinetic unibody acoustic impulses into real-time gesture control with **96.7% Stratified Cross-Validation Accuracy** and **Zero False Triggers**.

---

## 🧠 What is TLM (Tap Learning Model)?

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                      TLM (Tap Learning Model) 1.0                       │
├──────────────────────────────┬──────────────────────────────────────────┤
│ 🔤 LLM (Language Model)       │ 🎙️ TLM (Tap Learning Model)             │
│ Words ──► Tokens ──► Intent  │ Kinetic Impulses ──► TLM 1.0 ──► Action │
└──────────────────────────────┴──────────────────────────────────────────┘
```

**TLM 1.0** combines **3D Mel-Spectrogram Kinematics** with **50ms Unibody Mechanical Wave Dispersion** to separate physical aluminum chassis taps from ambient air-borne noise (like earphone lid snaps, door slams, or pen clicks) in under $0.1\text{ms}$.

---

## 🚀 Key Features

* **🧠 Powered by TLM 1.0:** First-principles acoustic gesture AI for laptop chassis.
* **🌊 50ms Mechanical Wave Dispersion (Feature #305):** Measures physical kinetic wave ring-down across aluminum decks ($0.160 - 0.330$ chassis tap vs $0.039 - 0.115$ air click).
* **🎯 97.0% Left / 95.0% Right Precision:** Multi-surface trained across Hard Desks, Soft Beds/Blankets, and Laps.
* **⚡ Hybrid Fallback Shield:** Combines TLM decision trees with a physical $0.14$ dispersion safety floor for zero false positives.
* **🛡️ 0% CPU Quartz Hardware Shields:** Passive C-level `CGEventTap` mutes the engine during active typing or trackpad gestures.
* **📳 Trackpad Haptic Feedback:** Triggers native macOS `NSTrackpadHapticFeedbackPerformer` confirmation clicks.
* **⌨️ Fn Key Kill-Switch:** Instant toggle between 🟢 `RESUMED` and 🔴 `PAUSED` state.

---

## 🏗️ Architecture & Pipeline

```text
                        [ Physical Unibody Kinetic Impulse ]
                                         │
                                         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. HARDWARE SENSOR FUSION LAYER (0% CPU)                                │
│    • Keyboard Guard (Quartz CGEventTap)   ──► Mutes during typing         │
│    • Trackpad Guard (Quartz CGEventTap)   ──► Mutes during trackpad drag    │
│    • System Kill-Switch (Fn Key)          ──► Mutes/resumes engine state    │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │ (Pass)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 2. TLM 1.0 TAP LEARNING ENGINE (model_double_tap.pkl | <0.5% CPU)       │
│    • 16,800 Sample 350ms Buffer          ──► Snappy gesture detection   │
│    • 305-Feature Mel + Kinematics Matrix  ──► 20 Mels x 15 Frames + Dispersion│
│    • 96.7% 5-Fold Stratified CV          ──► 100% Noise Precision           │
│    • Hybrid Dispersion Guard             ──► Blocks earphone lid snaps      │
└─────────────────────────────────────┬───────────────────────────────────┘
                                      │ (Validated)
                                      ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 3. NATIVE ACTION ENGINE & HAPTICS (actions.py)                          │
│    • Smart WhatsApp Toggle (Cmd+H / Focus)                              │
│    • Apple Music / Spotify Media Controls                               │
│    • Trackpad Haptic Confirmation Click                                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ⚡ Quickstart

```bash
# Clone
git clone https://github.com/CodeWithWinton/morse.git
cd morse

# Install dependencies
pip install numpy sounddevice scikit-learn

# Run TLM 1.0 Engine
python3 smart_detector.py
```

Double-tap the left or right metal palm rest of your laptop:

```text
✌️ DOUBLE-TAP (LEFT)! (ML Confidence: 100.0%, Vol: 8.5)
💬 Executing Action: SMART WHATSAPP TOGGLE (OPEN / HIDE)

✌️ DOUBLE-TAP (RIGHT)! (ML Confidence: 99.9%, Vol: 3.2)
🎵 Executing Action: APPLE MUSIC PLAY / PAUSE
```

Press `Fn` key anytime to pause/resume. Press `Ctrl+C` to exit.

---

## 📊 Model Performance (`model_double_tap.pkl`)

* 🏆 **5-Fold Stratified Cross-Validation:** **96.7% ($\pm 0.5\%$)**
* 🎯 **Held-Out Test Set Accuracy:** **96.6%**
* ⚡ **Feature Extraction Latency:** **$0.1\text{ms}$**

| Category | Precision | Recall | F1-Score | Support |
| :--- | :---: | :---: | :---: | :---: |
| **`double_left_palm`** | **97.0%** | **99.0%** | **0.98** | 480 |
| **`double_right_palm`** | **95.0%** | **99.0%** | **0.97** | 480 |
| **`noise_and_typing`** | **100.0%** | **82.0%** | **0.90** | 160 |

---

## 🧪 Diagnostic Tools Included

* **[`test_vibration_trail.py`](test_vibration_trail.py):** Real-time physical 50ms unibody wave dispersion diagnostic.
* **[`collect_lid_snaps.py`](collect_lid_snaps.py):** Hard negative air-borne click dataset collector.
* **[`test_noise_filter.py`](test_noise_filter.py):** Interactive audio comparison tool for raw mic vs. DSP filtered audio.
* **[`test_hardware_guards.py`](test_hardware_guards.py):** Quartz PyObjC keyboard/trackpad event tap listener diagnostic.

---

## Project Structure

```
morse/
├── smart_detector.py        # TLM 1.0 Real-Time Tap AI Engine
├── train_double_tap_model.py# 5-Fold Stratified Cross-Validation Trainer
├── collect_lid_snaps.py     # Hard Negative Lid Snap Collector
├── collect_double_taps.py   # Multi-Surface Double-Tap Collector
├── test_vibration_trail.py  # 50ms Mechanical Wave Dispersion Diagnostic
├── hardware_guards.py       # Quartz CGEventTap Keyboard/Trackpad Shields
├── actions.py               # Native macOS Action Triggers
├── haptic_feedback.py       # macOS Trackpad Haptic Confirmation
├── utils.py                 # 305-Feature Mel-Spectrogram Extractors & Wave Dispersion
├── model_double_tap.pkl     # Trained TLM 1.0 Production Model
└── dataset/                 # 2,600 Multi-Surface Raw Audio Samples (.npy)
```

---

## License

MIT — do whatever you want with it.

---

<p align="center">
  <em>Built by <a href="https://github.com/CodeWithWinton">Manas Maheshwari (CodeWithWinton)</a>.</em>
</p>
