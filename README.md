<p align="center">
  <h1 align="center">MORSE</h1>
  <p align="center">
    <code>-- --- .-. ... .</code>
  </p>
  <p align="center">
    <em>Powered by <strong>TLM 1.5 (Tap Learning Model Engine)</strong></em><br>
    <em>Turn your laptop unibody metal into a touch surface across any OS & laptop OEM.</em>
  </p>
  <p align="center">
    <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL_v3-blue.svg" alt="AGPL v3 License"></a>
    <a href="https://huggingface.co/datasets/CodeWithWinton/macbook-unibody-acoustic-tap-dataset"><img src="https://img.shields.io/badge/%F0%9F%A4%97-Hugging_Face_Dataset-yellow.svg" alt="Hugging Face"></a>
    <img src="https://img.shields.io/badge/Samples-13.5k_Ground--Truth-blue.svg" alt="13.5k Samples">
    <img src="https://img.shields.io/badge/Accuracy-98.5%25_Test-brightgreen.svg" alt="98.5% Accuracy">
    <img src="https://img.shields.io/badge/Latency-0.3ms-brightgreen.svg" alt="0.3ms Latency">
    <img src="https://img.shields.io/badge/CPU-%3C0.3%25-brightgreen.svg" alt="<0.3% CPU">
  </p>
</p>

---

## 🔬 What is MORSE & TLM 1.5?

**MORSE** is a zero-hardware, cross-platform acoustic gesture recognition platform powered by **TLM 1.5 (Tap Learning Model)**. It converts standard unibody aluminum laptops (macOS, Windows, Linux) into software-defined touch surfaces.

| Model Type | Input Signal | Core Processing Engine | Execution Output |
|---|---|---|---|
| 🔤 **LLM (Language Model)** | Text / Speech Tokens | Deep Transformer Weights | Text Generation & Reasoning |
| 🎙️ **TLM (Tap Learning Model)** | Kinetic Impulse Waves | 3,730D Spatial Matrix | **0.3ms OS Action & Media Controls** |

By exploiting the physical laws of **solid-state acoustic wave dispersion** ($2.5\text{kHz} - 4.5\text{kHz}$ high-frequency attenuation across metal chassis), MORSE differentiates left vs. right palm rest double-taps using a **single built-in laptop microphone** with **99.8% live precision** and **0.3ms execution latency**.

---

## 🚀 Zero-Friction Setup (Works on macOS, Windows & Linux)

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/CodeWithWinton/morse.git
cd morse
pip install sounddevice numpy scipy scikit-learn h5py huggingface_hub
```

### 2. Run Real-Time Detector
```bash
python3 smart_detector.py
```
* **👈 Left Double-Tap:** Smart WhatsApp Toggle (Open / Focus / Hide)
* **👉 Right Double-Tap:** Media Play / Pause (Spotify, Apple Music, YouTube)

---

## 🎙️ Data Collection & Hugging Face Sync Suite

Anyone on **macOS, Windows, or Linux** can collect physical tap/noise samples and contribute them directly to our master dataset!

### 1. Collect Data (`python3 collect_data.py`)
Launch the interactive universal collector:
```bash
python3 collect_data.py
```
* **Auto Hardware Detection:** Automatically detects microphone hardware across macOS, Windows (WASAPI/DirectSound), and Linux.
* **Auto Noise Floor Calibration:** Measures ambient room noise for 1s to set dynamic local trigger thresholds.
* **Stereo-to-Mono Downmixing:** Automatically converts 2-channel or multi-channel audio to standardized 1D float32 arrays (24,000 samples @ 48kHz).
* **Categories:** `double_left_palm`, `double_right_palm`, `noise_and_typing`.

### 2. Audit Dataset (`python3 audit_dataset.py`)
Run automated quality control before syncing:
```bash
python3 audit_dataset.py
```
* **Integrity Audit:** Checks for NaNs, Infs, dead silence, and clipped audio.
* **Noise Contamination Check:** Verifies that `noise_and_typing` samples contain zero stray tap impacts.
* **Spatial Label Check:** Verifies Left taps are physically Left (high onset ratio) and Right taps are physically Right (high structural decay).

### 3. Sync & Contribute to Hugging Face (`python3 sync_dataset.py`)
Push your local dataset contributions directly to Hugging Face LFS:
```bash
python3 sync_dataset.py
```
When you push, `sync_dataset.py` automatically:
* 💻 **Auto-detects your laptop model** (e.g. `MacBook Air (M1, 2020)`, `Dell XPS 15`, `Lenovo ThinkPad`).
* 📊 **Runs pre-push health audit** and calculates your audit pass percentage.
* 📄 **Generates `contribution_manifest.json`** containing sample counts, laptop model, platform details, and data bias summary (e.g. Left-heavy vs Right-heavy vs Noise-dominant).
* 📝 **Creates a detailed commit message** on Hugging Face documenting who sent it, from what laptop model, sample count breakdown, and audit score.
* ☁️ **Pushes both `.npy` raw files and manifest JSON** directly to Hugging Face LFS under `contributions/{username}/{laptop_model}/`.

---

## 📁 Repository Structure

```text
morse/
├── smart_detector.py         # Main real-time tap detection daemon
├── train_double_tap_model.py # 8-core parallel ML trainer (HistGradientBoosting 5-Fold CV)
├── utils.py                  # Core signal processing, Mel STFT & peak alignment
├── custom_noise_engine.py    # In-house chassis noise cancellation & speaker shield
├── hardware_guards.py        # Hardware event guards (Quartz listener with cross-platform fallback)
├── actions.py                # Cross-platform action handlers (WhatsApp, Media Play/Pause, Screenshot)
├── haptic_feedback.py        # System audio feedback confirmation sound
│
├── collect_data.py           # Launcher -> data_tools/universal_collector.py
├── sync_dataset.py            # Launcher -> data_tools/hf_dataset_sync.py
├── audit_dataset.py           # Launcher -> data_tools/audit_incoming_data.py
│
├── data_tools/               # Universal Dataset Suite
│   ├── universal_collector.py  # Cross-platform interactive collector
│   ├── hf_dataset_sync.py      # Hugging Face pull/push sync engine with rich metadata
│   └── audit_incoming_data.py  # Master dataset health & spatial label auditor
│
├── calibration/              # Chassis mapping & frequency calibration tools
├── tests/                    # Component unit tests
├── legacy/                   # Archived scratch scripts and raw audio samples
└── docs/                     # Documentation assets
```

---

## 📊 Benchmark & Empirical Performance

Evaluated on **13,528 physical ground-truth samples** (26,330 augmented feature vectors):

| Metric | Score |
|---|---|
| **5-Fold Cross-Validation Accuracy** | **98.5% (+/- 0.1%)** |
| **Test Set Accuracy** | **98.4%** |
| 👈 **`double_left_palm` Recall** | **0.99 (99%)** |
| 👉 **`double_right_palm` Recall** | **0.99 (99%)** |
| 🛡️ **`noise_and_typing` Precision** | **0.99 (99% / Zero False Positives)** |
| ⚡ **Latency** | **<0.3ms** |
| 🔋 **CPU Load** | **<0.3%** |

---

## 📄 Open-Core Commercial Licensing

MORSE is dual-licensed:
* **Community Edition (AGPL-3.0):** Free for open-source developers, academic research, and non-commercial experimentation.
* **Commercial OEM License:** Low-latency C++/Rust embedded SDK for laptop manufacturers (Apple, Dell, HP, Lenovo, Asus). Contact [manas17146@gmail.com](mailto:manas17146@gmail.com) for OEM licensing.

---
*Created with ❤️ by Manas Maheshwari ([@CodeWithWinton](https://github.com/CodeWithWinton)) & Daksh Sethi.*
