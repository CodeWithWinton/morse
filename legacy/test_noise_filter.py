import sounddevice as sd
import numpy as np
from scipy.io import wavfile
import time
import sys
import os

from utils import apply_medium_thud_dsp_filter, find_builtin_mic, SAMPLE_RATE

RECORD_SECONDS = 3.5

def main():
    device_id, dev_name = find_builtin_mic()
    print("==========================================================================")
    print("      MORSE - Medium-Tier Impulse Noise Filter Audio Comparison           ")
    print("==========================================================================")
    print(f"🎙️ Target Hardware: [{device_id}] {dev_name}")
    print("🎧 This tool records 3.5 seconds of audio and lets you HEAR the difference!")
    print("\n👉 Instructions:")
    print("   1. Play music or TV audio in the room, and perform a DOUBLE-TAP during recording.")
    print("   2. We will save 'raw_unfiltered.wav' and 'filtered_dsp.wav'.")
    print("   3. We will play both back through your speakers so you can compare!\n")
    
    input("Press ENTER to start recording for 3.5 seconds...")
    
    print("\n🔴 RECORDING NOW... (Double-tap palm rest while background audio plays!)")
    raw_audio = sd.rec(int(RECORD_SECONDS * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype=np.float32)
    sd.wait()
    print("✅ RECORDING COMPLETE!\n")
    
    sig = raw_audio.flatten()
    
    # Process signal through Medium-Tier DSP Noise Filter
    filtered_sig = apply_medium_thud_dsp_filter(sig)
    
    # Save both WAV files for inspection
    raw_path = "raw_unfiltered.wav"
    filtered_path = "filtered_dsp.wav"
    
    wavfile.write(raw_path, SAMPLE_RATE, (sig * 32767).astype(np.int16))
    wavfile.write(filtered_path, SAMPLE_RATE, (filtered_sig * 32767).astype(np.int16))
    
    print(f"💾 Saved: [raw_unfiltered.wav] & [filtered_dsp.wav]")
    
    print("\n--------------------------------------------------------------------------")
    print("🔊 PLAYING BACK: 1. RAW UNFILTERED AUDIO (Includes TV/speech/music)...")
    print("--------------------------------------------------------------------------")
    sd.play((sig * 0.9), SAMPLE_RATE)
    sd.wait()
    
    time.sleep(1.0)
    
    print("\n--------------------------------------------------------------------------")
    print("🎧 PLAYING BACK: 2. FILTERED DSP AUDIO (Medium-Tier Noise Suppressed)...")
    print("--------------------------------------------------------------------------")
    sd.play((filtered_sig * 0.9), SAMPLE_RATE)
    sd.wait()
    
    print("\n✨ Done! You can re-listen anytime or open 'filtered_dsp.wav' in Finder!")

if __name__ == "__main__":
    main()
