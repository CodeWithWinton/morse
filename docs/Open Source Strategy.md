# Open Source Strategy

[[Morse - Master Hub]] is designed as a 100% Free and Open Source Software (FOSS) project.

## Core Open Source Principles

### 1. Zero Cloud API Dependencies
* Morse runs **100% locally on-device** off-grid.
* No OpenAI API keys, no subscriptions, no external cloud calls.
* Zero privacy concerns (audio processed in local RAM and discarded immediately).

### 2. Zero Battery Drain
* Operates via [[DSP Engine]] math taking `< 0.01 ms` per frame.
* Runs continuously in the background without causing laptop cooling fans to spin.

### 3. Supply Chain & Code Trust
* **`git clone` Safety:** `git clone` copies text files to disk without running code.
* **Pure Python Source:** No mysterious pre-compiled `.exe` or `.dll` binary blobs. Every line of code is human-readable and inspectable.
* **Auto-Calibration:** Uses [[Auto-Calibration|morse calibrate]] so users never need to modify source code manually.

### 4. Cross-Platform Portability
* Built on `sounddevice` (PortAudio / WASAPI / CoreAudio) and `numpy`.
* Decoupled [[Architecture]] allows contributors to submit OS action adapters for macOS, Windows, and Linux.

Back to [[Morse - Master Hub]]
