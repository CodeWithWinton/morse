# Architecture

[[Morse - Master Hub]] uses a modular, decoupled architecture designed for cross-platform expansion and zero battery drain.

## Cascaded Two-Stage Engine

```
          [ Raw Audio Input Stream ]
                     │
                     ▼
          ┌─────────────────────┐
          │ Stage 1: DSP Gate   │  <-- Ultra-fast (0.01ms), 0% CPU
          │ ([[DSP Engine]])    │
          └──────────┬──────────┘
                     │
            (Passed DSP Gate?)
             ├── NO  ──> [ Silently Ignore / Drop Frame ]
             │
             └── YES ──> ┌──────────────────────────┐
                         │ Stage 2: ML Classifier   │ <-- Runs ONLY on candidate spikes!
                         │ ([[Machine Learning Model]]) │
                         └────────────┬─────────────┘
                                      │
                              (Confidence > 85%?)
                               ├── YES ──> 🎯 VERIFIED CHASSIS TAP!
                               └── NO  ──> 🔕 Rejection (False Alarm)
```

## Modular Subsystems

```
morse/
├── core/
│   ├── dsp_engine.py      # Audio input, FFT, and Tap Detection Engine
│   └── calibrator.py      # [[Auto-Calibration]] wizard
├── actions/
│   ├── macos_actions.py   # AppleScript / macOS triggers (Mute, Spotify, Raycast)
│   ├── windows_actions.py # WASAPI / Windows API triggers
│   └── linux_actions.py   # xdotool / Linux triggers
├── ui/
│   ├── web_dashboard/     # Sleek local Web UI (http://localhost:5000)
│   └── menubar/           # macOS Menu Bar systray icon
├── config.json            # User-customizable settings & calibrated thresholds
└── main.py                # Main daemon entry point
```

## User Experience Stack
1. **Background Daemon (`morse start`):** Runs lightweight detection loop (< 5MB RAM).
2. **macOS Menu Bar Systray Icon:** Quick toggle for Sensitivity (`Quiet`, `Party`, `Auto`) and Mute status.
3. **Local Web Dashboard (`http://localhost:5000`):** Modern dark-mode UI with live oscilloscope waveform visualizer, gesture dropdown mapper, and calibration wizard.

Back to [[Morse - Master Hub]]
