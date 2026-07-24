# Core Technology

Morse detects physical chassis taps using the laptop's **internal microphone** as a Software-Defined Virtual Accelerometer. No external hardware, no cloud APIs.

## The Physics
When a finger taps the aluminum chassis of a MacBook (or any metal/plastic laptop body), the physical impact creates a **structural shockwave** that travels through the solid frame directly to the internal microphone.

This shockwave has a unique acoustic fingerprint:
* **Dominant frequency:** 100–600 Hz (sub-bass aluminum resonance).
* **Duration:** < 10 milliseconds (instantaneous impulse).
* **Decay:** Near-zero energy in the frame immediately after the spike.

## How It Differs From Other Sounds

| Sound Source | Low Freq (100–600 Hz) | High Freq (> 1500 Hz) | Duration | Decay |
| :--- | :--- | :--- | :--- | :--- |
| **Chassis Tap** | Very High | Low | < 10 ms | Instant |
| **Keyboard Typing** | Low | Very High (plastic click) | 20–50 ms | Gradual |
| **TV / Speech** | Medium | Medium | 200–500 ms | Sustained |
| **Aarti Bell** | Low | Very High (metallic chime) | 500 ms+ | Slow ring |

## The Software Stack
* **Language:** Python 3
* **Audio Input:** `sounddevice` (backed by PortAudio — cross-platform)
* **Signal Processing:** `numpy` (FFT, RMS, peak detection)
* **Zero Heavy Dependencies:** No TensorFlow, no PyTorch, no cloud APIs.

## Detection Pipeline
Raw audio flows through the [[DSP Engine]], which extracts frequency ratio, crest factor, and transient decay. See [[Architecture]] for the full Cascaded Two-Stage pipeline.

## Hardware Compatibility
* Works on **any laptop** with an internal microphone (Mac, Windows, Linux).
* See [[Hardware Discovery]] for why we pivoted from the accelerometer.

Back to [[Morse - Master Hub]]
