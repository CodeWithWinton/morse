import sounddevice as sd
import numpy as np
import time
import os
from scipy.io import wavfile
from utils import find_builtin_mic, SAMPLE_RATE, WINDOW_SIZE

print("====================================")
print("   MORSE - Audio & Spectrogram Inspector ")
print("====================================")

builtin_id, dev_name = find_builtin_mic()
print(f"🎙️ Target Hardware: [{builtin_id}] {dev_name}")
print("⏳ Preparing 3-second recording in 1 second...")
time.sleep(1.0)

print("\n🔴 RECORDING NOW! Make a double-tap, talk out loud, or play music!")
audio_data = sd.rec(int(3.0 * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, device=builtin_id)
sd.wait()
print("🟢 Recording finished! Processing 2D Spectrogram Filter...\n")

raw_signal = audio_data.flatten()

# Save raw audio file
raw_filename = "raw_tap.wav"
wav_int16_raw = np.int16(raw_signal / (np.max(np.abs(raw_signal)) + 1e-6) * 32767)
wavfile.write(raw_filename, SAMPLE_RATE, wav_int16_raw)
print(f"💾 Saved Raw Audio: [raw_tap.wav](file://{os.path.abspath(raw_filename)})")

# 10ms Chunk RMS Thresholding (Forces all background noise blocks to absolute digital zero!)
chunk_size = 480  # 10ms at 48kHz
num_chunks = len(raw_signal) // chunk_size
chunk_rms = np.array([np.sqrt(np.mean(raw_signal[i*chunk_size:(i+1)*chunk_size]**2)) for i in range(num_chunks)])
median_rms = np.median(chunk_rms) + 1e-6

filtered_signal = np.zeros_like(raw_signal)

# Smooth 5ms Fade Envelope (Eliminates step-discontinuity clicks and distortion!)
fade_len = 240  # 5ms at 48kHz
fade_in = np.sin(np.linspace(0, np.pi/2, fade_len))**2
fade_out = np.cos(np.linspace(0, np.pi/2, fade_len))**2

for i in range(num_chunks):
    start = i * chunk_size
    end = start + chunk_size
    chunk = raw_signal[start:end].copy()
    
    # If 10ms chunk RMS is 2.0x higher than median background noise, keep it!
    if chunk_rms[i] >= (median_rms * 2.0):
        # Apply smooth 5ms fade envelope at edges to prevent click distortion
        if len(chunk) >= 2 * fade_len:
            chunk[:fade_len] *= fade_in
            chunk[-fade_len:] *= fade_out
        filtered_signal[start:end] = chunk
    else:
        # ABSOLUTE DIGITAL ZERO (100% Mute)
        filtered_signal[start:end] = 0.0

# Save 100% suppressed audio file
filtered_filename = "filtered_tap.wav"
wav_int16_filt = np.int16(np.clip(filtered_signal, -1.0, 1.0) * 32767)
wavfile.write(filtered_filename, SAMPLE_RATE, wav_int16_filt)
print(f"⚡ Saved 100% Background-Muted Audio: [filtered_tap.wav](file://{os.path.abspath(filtered_filename)})")

print("\n🎧 LISTEN TO THE DIFFERENCE:")
print(f"  1. Double-click raw_tap.wav to hear raw mic audio.")
print(f"  2. Double-click filtered_tap.wav to hear 90%+ suppressed audio!\n")
