# Morse (`-- --- .-. ... .`)

**Concept:** Turn the MacBook chassis (and eventually the surrounding physical desk) into a gesture-sensitive trackpad using the internal accelerometer.

## Core Pillars
* [[Core Technology]] - How we actually get the data from the hardware.
* [[Machine Learning Model]] - How we stop false positives (typing vs tapping).
* [[Future Roadmap]] - Where this project is going (Desk Mode, Sensor Fusion).

## Why This Matters
Right now, tap-based apps rely on simple math thresholds (if vibration > 1.2Gs, do action). This leads to massive false positives when typing. Morse solves this by treating it as an Applied Data Science problem.
