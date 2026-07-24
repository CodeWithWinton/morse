import sounddevice as sd
import numpy as np
import time
import actions

SAMPLE_RATE = 44100
last_tap_time = 0

event_counter = 0

def audio_callback(indata, frames, time_info, status):
    global last_tap_time, event_counter
    sig = indata.flatten()
    volume = np.linalg.norm(sig) * 10
    
    # Check any sound above ambient noise floor and below clipping ceiling
    if 10.0 <= volume <= 130.0:
        current_time = time.time()
        if current_time - last_tap_time > 0.3:
            event_counter += 1
            
            # Isolate Peak Transient Window
            peak_idx = np.argmax(np.abs(sig))
            start_idx = max(0, peak_idx - 50)
            end_idx = min(len(sig), peak_idx + 800)
            transient = sig[start_idx:end_idx]
            
            fft_vals = np.abs(np.fft.rfft(transient))
            freqs = np.fft.rfftfreq(len(transient), d=1.0/SAMPLE_RATE)
            
            # 120Hz Sub-Bass Wind Cutoff (Eliminates breath plosives < 100Hz)
            bass_energy = np.sum(fft_vals[(freqs >= 120) & (freqs <= 600)])
            high_energy = np.sum(fft_vals[freqs > 1500]) + 1e-6
            ratio = bass_energy / high_energy
            
            # Impulsiveness (Peak / RMS)
            rms = np.sqrt(np.mean(transient**2)) + 1e-6
            peak = np.max(np.abs(transient))
            crest_factor = peak / rms
            
            # 2-Tier Aluminum Master Rule:
            # Tier 1: High Resonance Chassis Tap (Ratio >= 3.0) -> Always Tap
            # Tier 2: Soft Chassis Tap (Ratio >= 1.8 & Crest >= 2.0 & High Energy < 35.0)
            is_tap = (10.0 <= volume <= 130.0) and (
                (ratio >= 3.0) or 
                (ratio >= 1.8 and crest_factor >= 2.0 and high_energy < 35.0)
            )
            
            if is_tap:
                print(f"\n🎯 CHASSIS TAP DETECTED! (Event #{event_counter:03d} -> Ratio: {ratio:.2f}, Vol: {volume:.1f})")
                actions.execute_action("music")
                last_tap_time = current_time
            else:
                print(f"   [Filtered] Event #{event_counter:03d} -> Ratio: {ratio:.2f}, Vol: {volume:.1f}")

# Explicitly find and select Built-in Microphone hardware device
devices = sd.query_devices()
builtin_device_id = None
for i, dev in enumerate(devices):
    if dev['max_input_channels'] > 0 and ("built-in" in dev['name'].lower() or "macbook" in dev['name'].lower()):
        builtin_device_id = i
        print(f"🎙️ Target Hardware: [{i}] {dev['name']}")
        break

if builtin_device_id is None:
    print("⚠️ Could not find Built-in Microphone name, using system default.")

print("====================================")
print("   MORSE - Ponytail DSP Tap Filter  ")
print("====================================")
print("🎙️  Listening to chassis... (Tap metal, type, or ring bell!)")
print("Press Ctrl+C to stop.\n")

try:
    with sd.InputStream(device=builtin_device_id, samplerate=SAMPLE_RATE, channels=1, callback=audio_callback):
        sd.sleep(1000000)
except KeyboardInterrupt:
    print("\nStopping...")
