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
    <img src="https://img.shields.io/badge/Network-Offline-purple.svg" alt="100% Offline">
  </p>
</p>

---

**Morse** is a software-defined acoustic tap engine that turns your laptop chassis into a touch surface. Double-tap the metal body of your MacBook and Morse will play/pause your music, mute your mic, or trigger any shortcut you want — no special hardware required.

It works by listening to the built-in microphone for the unique low-frequency vibration that aluminum produces when you tap it, then filtering out everything else (typing, speech, wind, room noise) using a lightweight DSP pipeline that runs at **0% CPU overhead**.

## Why Morse Exists

Every commercial tap-detection app on macOS (QuickTap, Knock, etc.) relies on the **SPU accelerometer** — a physical chip that only ships in M2/M3/M4 MacBooks. If you have a base M1 MacBook Air, an Intel Mac, or literally any non-Apple laptop, those apps don't work at all.

Morse takes a different approach: **pure acoustic signal processing through the mic you already have.** It works on every laptop with a microphone.

## How It Works

```
Audio Stream (Built-in Mic)
        │
        ▼
┌───────────────────────────────────┐
│   Stage 1: Ponytail DSP Filter    │  ← Runs on every audio frame
│                                   │     0% CPU, < 0.01ms latency
│  • 120 Hz wind cutoff             │
│  • Crest factor impulse check     │
│  • Bass/treble ratio analysis     │
│  • Typing interruption reset      │
│  • Double-tap pattern matcher     │
│    (40ms – 750ms window)          │
└───────────────┬───────────────────┘
                │
      [Candidate double-tap?]
                │
                ▼
┌───────────────────────────────────┐
│   Stage 2: ML Classifier (WIP)   │  ← Wakes only on candidates
│                                   │     Pushes accuracy 89% → 99%+
│  • Transient spectrogram eval     │
│  • Edge case disambiguation       │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│   Native macOS Action Engine      │
│                                   │
│  • Apple Music play/pause         │
│  • System volume mute/unmute      │
│  • Raycast launcher trigger       │
│  • (Extensible via actions.py)    │
└───────────────────────────────────┘
```

## Quickstart

```bash
# Clone
git clone https://github.com/CodeWithWinton/morse.git
cd morse

# Install dependencies (just two — numpy and sounddevice)
pip install numpy sounddevice

# Run
python3 stream_audio.py
```

Double-tap the metal chassis of your laptop. You should see:

```
 👆 Tap 1 captured... (Event #001 -> Ratio: 3.02, Vol: 14.2)

✌️ DOUBLE-TAP DETECTED! (Event #002 -> Ratio: 2.89, Vol: 12.8)
🎵 Executing Action: APPLE MUSIC PLAY / PAUSE
```

Press `Ctrl+C` to stop.

## The Physics

When you tap the aluminum unibody of a MacBook, the impact creates a structural shockwave that resonates between **120 Hz and 600 Hz** — a frequency band that typing, speech, and wind turbulence don't occupy in the same way.

Morse exploits five acoustic invariants to separate real taps from everything else:

| Signal | Bass Ratio (120–600 Hz) | Crest Factor | Volume |
|---|---|---|---|
| **Chassis tap** | 1.5 – 10.0+ | ≥ 2.0 | 10 – 110 |
| Keyboard typing | 0.05 – 1.2 | varies | 10 – 90 |
| Speech / singing | 0.8 – 1.4 | < 2.0 | 10 – 80 |
| Blowing into mic | 1.0 – 8.0 | < 1.9 | 80 – 1250 |
| Room noise | 0.0 – 0.8 | < 1.5 | 5 – 15 |

The double-tap pattern (two taps within 750ms) adds a temporal dimension that eliminates accidental single bumps entirely.

## Project Structure

```
morse/
├── stream_audio.py     # Main engine — run this
├── actions.py          # macOS action triggers (AppleScript)
├── collect_data.py     # Dataset recorder for ML training
├── docs/               # Obsidian vault (architecture notes)
├── dataset/            # Recorded tap/noise samples (.npy)
└── LICENSE             # MIT
```

## Architecture Evolution & Empirical Lessons

| Iteration | Approach | Benchmark Result | Engineering Finding / Pivot |
|---|---|---|---|
| **v1.0** | Single-Tap Pure DSP | High False Positives (~40%) | Single-tap lacks temporal context; soft taps and palm rests overlap in 1D audio amplitude. **Pivot:** Double-Tap pattern matcher ($150\text{ms} - 650\text{ms}$). |
| **v2.0** | Truncated $5.8\text{ms}$ ML | 66.4% Accuracy | $5.8\text{ms}$ slices truncated the tail end of aluminum resonance. **Pivot:** Upgraded buffer to $46.4\text{ms}$ (2048 samples). |
| **v3.0** | 12 Hand-crafted Features | 78.9% Accuracy | Feature compression lost exact harmonic spectrum shape. **Pivot:** Switched to raw 1025-bin normalized FFT magnitude spectrum. |
| **v4.0 (Current)** | 2048-Sample Raw Spectrogram + Two-Stage Engine | **87.6% ML / 98.5%+ Pipeline** | Full $46.4\text{ms}$ acoustic resolution fed to `HistGradientBoosting` ($31\mu\text{s}$ latency) gated by Stage 1 Ponytail DSP ($0\%$ CPU). |

## Current Status

- ✅ Double-tap gesture engine with **98.5%+ real-world precision**
- ✅ Stage 1 Ponytail DSP Candidate Filter ($0\%$ CPU overhead)
- ✅ Stage 2 `HistGradientBoosting` ML Classifier ($31\mu\text{s}$ latency, trained on 4,778 samples)
- ✅ Smart Window Toggle (Open / Hide WhatsApp via `Cmd+H`)
- ✅ Built-in microphone hardware lock (ignores external headsets/mics)
- ✅ Instant `Ctrl+C` clean exit
- 🔧 `morse calibrate` auto-calibration wizard (planned)
- 🔧 Desk mode with spatial TDOA localization (planned)

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
