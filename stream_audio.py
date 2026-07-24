import sounddevice as sd
import numpy as np
import time

last_tap_time = 0

def audio_callback(indata, frames, time_info, status):
    global last_tap_time
    
    # Calculate the volume
    volume = np.linalg.norm(indata) * 10
    
    # If it's a loud spike
    if volume > 5:
        current_time = time.time()
        # DEBOUNCER: Ignore any spikes that happen within 0.3 seconds of the last one
        if current_time - last_tap_time > 0.3:
            print(f"🎯 SINGLE CHASSIS TAP DETECTED! (Volume: {volume:.1f})")
            last_tap_time = current_time

print("====================================")
print("   MORSE - Debounced Tap Detection  ")
print("====================================")
print("🎙️  Listening to chassis... (Tap the metal!)")
print("Press Ctrl+C to stop.")

try:
    with sd.InputStream(callback=audio_callback):
        sd.sleep(1000000)
except KeyboardInterrupt:
    print("\nStopping...")
