# Core Technology

To read physical taps on the chassis, we must bypass standard macOS APIs and read directly from the IOKit registry.

## The Hardware
* **Sensor:** `AppleSPUHIDDevice` (Apple Silicon only).
* **Location:** Built-in MEMS accelerometer and gyroscope managed by the Sensor Processing Unit (SPU).
* **Data Format:** 3-axis (X, Y, Z) acceleration output at ~800Hz.

## The Software Stack
* **Language:** Python (for MVP and Data Science modeling).
* **Libraries:** We are utilizing `macimu` (by olvvier) to handle the complex C-level IOKit bindings and `sudo` root access requirements.
* **Dependencies:** `hidapi`, `macimu`

Back to [[Morse - Master Hub]]
