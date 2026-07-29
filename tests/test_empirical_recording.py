import sounddevice as sd
import numpy as np
import time
import sys
import os
from scipy.io import wavfile

from custom_noise_engine import CustomChassisNoiseEngine
from utils import find_builtin_mic, SAMPLE_RATE

RECORD_SECONDS = 5
FRAME_SIZE = 16800  # 350ms window at 48kHz

def record_empirical_audio(mode_name="General"):
    print("\n==========================================================================")
    print(f" 🎙️ MORSE EMPIRICAL NOISE TEST: {mode_name.upper()}")
    print("==========================================================================")
    
    builtin_id, dev_name = find_builtin_mic()
    print(f"🎙️ Target Input Device: [{builtin_id}] {dev_name}")
    print(f"⏱️ Recording Duration : {RECORD_SECONDS} seconds")
    print(f"🎧 Custom Noise Engine : ACTIVE (< 0.9% CPU)")
    print("\n⚠️ Get ready... Recording will start in 3 seconds!")
    for t in range(3, 0, -1):
        print(f"  {t}...", flush=True)
        time.sleep(1)
        
    print("\n🔴 RECORDING NOW! Double-tap your palm rest while noise/music is playing! 🔴\n")
    
    engine = CustomChassisNoiseEngine(sample_rate=SAMPLE_RATE)
    
    # Record raw audio stream
    total_samples = int(RECORD_SECONDS * SAMPLE_RATE)
    raw_audio = sd.rec(total_samples, samplerate=SAMPLE_RATE, channels=1, device=builtin_id, dtype=np.float32)
    
    for elapsed in range(1, RECORD_SECONDS + 1):
        time.sleep(1)
        print(f"  • Recording... [{elapsed}/{RECORD_SECONDS}s]", flush=True)
        
    sd.wait()
    raw_signal = raw_audio.flatten()
    print("✅ Recording Completed!")

    print("\n⚙️ Processing raw audio stream through Custom Noise Engine...")
    filtered_signal = np.zeros_like(raw_signal)
    
    # Process in rolling 350ms frames
    step = int(0.05 * SAMPLE_RATE)  # 50ms hop
    frame_len = FRAME_SIZE
    
    for i in range(0, len(raw_signal) - frame_len, step):
        chunk = raw_signal[i:i + frame_len]
        clean_chunk, stats = engine.process_frame(chunk)
        filtered_signal[i:i + frame_len] = clean_chunk

    # Normalize volume scaling for export
    raw_norm = np.int16(raw_signal / max(np.max(np.abs(raw_signal)), 1e-6) * 32767)
    filt_norm = np.int16(filtered_signal / max(np.max(np.abs(filtered_signal)), 1e-6) * 32767)
    
    raw_path = f"empirical_raw_{mode_name.lower()}.wav"
    filt_path = f"empirical_filtered_{mode_name.lower()}.wav"
    
    wavfile.write(raw_path, SAMPLE_RATE, raw_norm)
    wavfile.write(filt_path, SAMPLE_RATE, filt_norm)
    
    # Calculate empirical SNR & Noise Attenuation metrics
    raw_rms = np.sqrt(np.mean(raw_signal ** 2)) + 1e-6
    filt_rms = np.sqrt(np.mean(filtered_signal ** 2)) + 1e-6
    attenuation_db = 20 * np.log10(raw_rms / filt_rms)
    
    raw_peak = np.max(np.abs(raw_signal))
    filt_peak = np.max(np.abs(filtered_signal))
    
    print("\n==========================================================================")
    print(" 📊 EMPIRICAL AUDIO METRICS REPORT")
    print("==========================================================================")
    print(f"  • Raw Mic Audio Peak      : {raw_peak:.4f} (RMS: {raw_rms:.4f})")
    print(f"  • Custom Filtered Peak    : {filt_peak:.4f} (RMS: {filt_rms:.4f})")
    print(f"  • Noise Floor Attenuation : {attenuation_db:.2f} dB Reduction")
    print("\n💾 SAVED TEST AUDIO FILES:")
    print(f"  1. Raw Unfiltered WAV  : file://{os.path.abspath(raw_path)}")
    print(f"  2. Custom Filtered WAV : file://{os.path.abspath(filt_path)}")
    print("\n🎧 Play both WAV files to compare raw mic noise vs cleaned tap audio by ear!\n")

def main():
    print("==========================================================================")
    print("   MORSE - Live Empirical Audio Testing Suite                             ")
    print("==========================================================================")
    print("Select test mode:")
    print("  1. Test Mode A: MacBook Speaker Music / YouTube Video Test")
    print("  2. Test Mode B: External Background Noise (Fan / Speech / AC) Test")
    print("  3. Exit")
    
    choice = input("\nEnter choice (1, 2, or 3): ").strip()
    if choice == "1":
        record_empirical_audio("speaker_music")
    elif choice == "2":
        record_empirical_audio("background_noise")
    else:
        print("Exiting test tool.")

if __name__ == "__main__":
    main()
