import sounddevice as sd
import numpy as np
import time

SAMPLE_RATE = 44100

print("====================================")
print("   MORSE - Dual-Mic Differential Test")
print("====================================")

# Find Built-in Microphone device
devices = sd.query_devices()
builtin_device_id = None
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0 and ("built-in" in dev['name'].lower() or "macbook" in dev['name'].lower()):
        builtin_device_id = i
        print(f"🎙️ Found Hardware: [{i}] {dev['name']} (Max Channels: {dev['max_input_channels']})")
        break

def callback(indata, frames, time_info, status):
    if indata.shape[1] >= 2:
        mic_left = indata[:, 0]
        mic_right = indata[:, 1]
        
        vol_left = np.linalg.norm(mic_left) * 10
        vol_right = np.linalg.norm(mic_right) * 10
        
        diff = mic_left - mic_right
        vol_diff = np.linalg.norm(diff) * 10
        
        if max(vol_left, vol_right) > 8.0:
            print(f"🔊 Vol L: {vol_left:.1f} | Vol R: {vol_right:.1f} | Differential (L-R): {vol_diff:.1f}")

try:
    print("\n🎙️ Listening in STEREO Dual-Mic Mode (channels=2)...")
    print("Press Ctrl+C to stop.\n")
    with sd.InputStream(device=builtin_device_id, samplerate=SAMPLE_RATE, channels=2, callback=callback):
        while True:
            sd.sleep(1000)
except KeyboardInterrupt:
    print("\n👋 Stopped Dual-Mic test cleanly.")
except Exception as e:
    print(f"\n❌ Stereo stream error: {e}")
