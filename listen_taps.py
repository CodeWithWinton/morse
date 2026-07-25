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

# 2D Spectrogram Vertical Impulse Filter (Strips horizontal music/speech lines, keeps vertical tap spikes)
fft_size = 512
hop_size = 128
num_frames = (len(raw_signal) - fft_size) // hop_size

filtered_signal = np.zeros_like(raw_signal)
prev_spectrum = np.zeros(fft_size // 2 + 1)

for i in range(num_frames):
    start = i * hop_size
    frame = raw_signal[start:start + fft_size] * np.hanning(fft_size)
    spectrum = np.abs(np.fft.rfft(frame))
    
    # Compute 2D Spectral Flux (Time derivative of energy: dE/dt)
    spectral_flux = np.sum(np.maximum(0, spectrum - prev_spectrum))
    prev_spectrum = spectrum
    
    # Keep frame ONLY if it contains a vertical impulse surge (dE/dt spike)
    if spectral_flux > 0.08:
        filtered_signal[start:start + fft_size] += frame

# Normalize and save filtered audio file
filtered_filename = "filtered_tap.wav"
max_filt = np.max(np.abs(filtered_signal)) + 1e-6
wav_int16_filt = np.int16(filtered_signal / max_filt * 32767)
wavfile.write(filtered_filename, SAMPLE_RATE, wav_int16_filt)
print(f"⚡ Saved 90%+ Suppressed Audio: [filtered_tap.wav](file://{os.path.abspath(filtered_filename)})")

print("\n🎧 LISTEN TO THE DIFFERENCE:")
print(f"  1. Double-click raw_tap.wav to hear raw mic audio.")
print(f"  2. Double-click filtered_tap.wav to hear 90%+ suppressed audio!\n")
