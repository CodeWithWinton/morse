import sounddevice as sd
import numpy as np
import time

SAMPLE_RATE = 44100
last_tap_time = 0

def audio_callback(indata, frames, time_info, status):
    global last_tap_time
    sig = indata.flatten()
    volume = np.linalg.norm(sig) * 10
    
    # 1. Volume threshold check
    if volume > 4.5:
        current_time = time.time()
        # 2. Debounce (350ms)
        if current_time - last_tap_time > 0.35:
            # 3. Ponytail DSP: Low-Note (100-400 Hz Chassis Resonance) Filter
            fft_vals = np.abs(np.fft.rfft(sig))
            freqs = np.fft.rfftfreq(len(sig), d=1.0/SAMPLE_RATE)
            
            # Isolate Low Notes (100-400 Hz Chassis Resonance) & High Click Noise (>2000 Hz)
            bass_energy = np.sum(fft_vals[(freqs >= 100) & (freqs <= 400)])
            high_energy = np.sum(fft_vals[freqs > 2000])
            
            # Production DSP Filter:
            # 1. Volume > 12.0 & Bass > 20.0 (Chassis structural shockwave)
            # 2. High Energy < 15.0 (Rejects key slamming plastic clicks)
            if volume > 12.0 and bass_energy > 20.0 and high_energy < 15.0:
                print(f"🎯 CHASSIS TAP DETECTED! (Bass: {bass_energy:.1f}, High: {high_energy:.1f}, Vol: {volume:.1f})")
                last_tap_time = current_time

print("====================================")
print("   MORSE - Ponytail DSP Tap Filter  ")
print("====================================")
print("🎙️  Listening to chassis... (Tap metal, type, or ring bell!)")
print("Press Ctrl+C to stop.\n")

try:
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, callback=audio_callback):
        sd.sleep(1000000)
except KeyboardInterrupt:
    print("\nStopping...")
