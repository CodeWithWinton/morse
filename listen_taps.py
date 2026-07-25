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

# Block-level Spectral Flux Gate (Eliminates overlap-add phase distortion!)
block_size = 2048
num_blocks = len(raw_signal) // block_size
filtered_signal = np.zeros_like(raw_signal)
prev_spectrum = np.zeros(block_size // 2 + 1)

for b in range(num_blocks):
    start = b * block_size
    end = start + block_size
    block = raw_signal[start:end]
    
    rms = np.sqrt(np.mean(block**2)) + 1e-6
    peak = np.max(np.abs(block))
    crest = peak / rms
    
    fft_vals = np.abs(np.fft.rfft(block * np.hanning(block_size)))
    freqs = np.fft.rfftfreq(block_size, d=1.0/SAMPLE_RATE)
    
    hp_energy = np.sum(fft_vals[freqs >= 2500]) + 1e-6
    hp_ratio = hp_energy / (np.sum(fft_vals) + 1e-6)
    
    # Is it a real physical tap impulse? (Crest >= 2.2 OR High-Pass >= 18%)
    is_tap = (crest >= 2.2) or (hp_ratio >= 0.18 and crest >= 1.6)
    
    if is_tap:
        # Keep physical tap at 100% full volume!
        filtered_signal[start:end] = block
    else:
        # Suppress background music/speech by 99% (0.01x volume)!
        filtered_signal[start:end] = block * 0.01

# Save 90%+ suppressed audio file with 100% crystal-clear tap sound
filtered_filename = "filtered_tap.wav"
wav_int16_filt = np.int16(np.clip(filtered_signal, -1.0, 1.0) * 32767)
wavfile.write(filtered_filename, SAMPLE_RATE, wav_int16_filt)
print(f"⚡ Saved 90%+ Suppressed Audio: [filtered_tap.wav](file://{os.path.abspath(filtered_filename)})")

print("\n🎧 LISTEN TO THE DIFFERENCE:")
print(f"  1. Double-click raw_tap.wav to hear raw mic audio.")
print(f"  2. Double-click filtered_tap.wav to hear 90%+ suppressed audio!\n")
