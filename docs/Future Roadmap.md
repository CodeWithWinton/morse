# Future Roadmap

Once the core chassis tap detection is perfected, Morse will expand into a magical spatial computing tool.

## Phase 1: Desk Mode (Acoustic + Vibration)
Turn the physical table around the MacBook into a gesture zone. 
* **How:** The accelerometer is sensitive enough to feel vibrations traveling through a wooden desk and up the rubber feet of the Mac.
* **Sensor Fusion:** In the future, we will combine the accelerometer data with the **Internal Microphone** to listen for the "thud" of a desk tap. Combining audio and vibration creates a 99.9% accurate gesture profile.

## Phase 2: Windows Port
Expand the market to PC users.
* **How:** Utilize the Windows Sensor API to read built-in accelerometers found in 2-in-1 laptops (like the Surface Pro).
* **Challenge:** Hardware fragmentation. Requires a robust "Calibration Mode" for users to train the ML model on their specific laptop chassis.

Back to [[Morse - Master Hub]]
