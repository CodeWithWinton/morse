import sounddevice as sd
import numpy as np
import time
import sys
import actions

SAMPLE_RATE = 44100
last_tap_time = 0
last_tap_ratio = 0.0
event_counter = 0

def audio_callback(indata, frames, time_info, status):
    global last_tap_time, last_tap_ratio, event_counter
    sig = indata.flatten()
    volume = np.linalg.norm(sig) * 10
    
    # Check sound above ultra-soft touch noise floor (4.0) and below clipping ceiling
    if 4.0 <= volume <= 80.0:
        current_time = time.time()
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
        
        # Ultra-Soft Candidate Gate (Vol: 4-80, Ratio >= 0.70, Crest >= 1.2)
        is_candidate_tap = (4.0 <= volume <= 80.0) and (ratio >= 0.70) and (crest_factor >= 1.2)
        
        if is_candidate_tap:
            time_since_last = current_time - last_tap_time
            if 0.05 < time_since_last < 1.0:
                # Fail-Safe Verification: Ensure at least one tap has metal chassis resonance (Ratio >= 0.85)
                if (ratio >= 0.85) or (last_tap_ratio >= 0.85):
                    print(f"\n✌️ DOUBLE-TAP DETECTED! (Event #{event_counter:03d} -> Ratio: {ratio:.2f}, Vol: {volume:.1f})")
                    actions.execute_action("whatsapp")
                    last_tap_time = 0
                    last_tap_ratio = 0.0
                else:
                    print(f"   [Fail-Safe Blocked] Typing key sequence detected (Ratio 1: {last_tap_ratio:.2f}, Ratio 2: {ratio:.2f})")
                    last_tap_time = current_time
                    last_tap_ratio = ratio
            elif time_since_last <= 0.05 and last_tap_time > 0:
                # Ignore follow-up ringing blocks from the exact same physical tap (< 50ms)
                pass
            else:
                print(f" 👆 Tap 1 captured... (Event #{event_counter:03d} -> Ratio: {ratio:.2f}, Vol: {volume:.1f})")
                last_tap_time = current_time
                last_tap_ratio = ratio
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
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\n👋 Stopping Morse cleanly...")
    sys.exit(0)
