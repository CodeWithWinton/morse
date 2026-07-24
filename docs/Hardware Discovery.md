# Hardware Discovery

During early development of [[Morse - Master Hub]], we attempted to read physical tap data directly from the MacBook's internal accelerometer.

## The Accelerometer Investigation
* **Initial Plan:** Hook into the macOS `IOKit` registry using `macimu` and `hidapi` to stream raw 800Hz 3-axis accelerometer data from `AppleSPUHIDDevice`.
* **The Problem:** When running `stream_data.py` on an **M1 MacBook Air**, the device opened successfully but produced zero data frames (resulting in timeouts).
* **The Root Cause Analysis:** Running kernel diagnostics via `ioreg -l | grep -i "spu"` revealed:
  * Active SPU nodes: `als` (Ambient Light Sensor), `wakehint` (lid sensor), `aop-audio` (mic), `aop-voicetrigger`.
  * **Missing nodes:** No `accel` or `gyro` endpoints exist in the IOKit tree for base M1 MacBook Air models.

## Hardware Reality vs. High-End Models
* Base M1 MacBook Air models physically lack the accelerometer chip on the motherboard.
* Higher-end Apple Silicon Macs (M2, M3, Pro/Max series) include the full sensor array.

## The Pivotal Senior Dev Decision
Relying on physical accelerometers would limit Morse to high-end Mac models, excluding millions of MacBook Air, Intel Mac, and Windows laptop users.

We pivoted to using the **internal microphone** as a Software-Defined Virtual Accelerometer, unlocking 100% universal laptop compatibility. See [[Core Technology]] for the physics.

Back to [[Morse - Master Hub]]
