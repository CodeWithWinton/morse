import sounddevice as sd
import numpy as np
import time
from aec_engine import AECEngine
from utils import find_builtin_mic, SAMPLE_RATE, WINDOW_SIZE

print("====================================")
print("   MORSE - Speaker & Room AEC Test  ")
print("====================================")

aec = AECEngine(sample_rate=SAMPLE_RATE)
builtin_id, dev_name = find_builtin_mic()
print(f"🎙️ Target Hardware: [{builtin_id}] {dev_name}")
print("\n🔊 INSTRUCTIONS FOR TEST:")
print("  1. Play YouTube / Spotify music out of your Mac speakers!")
print("  2. Talk out loud or hum!")
print("  3. Double-tap your metal palm rest!\n")
print("⏳ Starting in 1 second...")
time.sleep(1.0)
print("🔴 LISTENING NOW! Press Ctrl+C to stop.\n")

buffer = np.zeros(WINDOW_SIZE)

def callback(indata, frames, time_info, status):
    global buffer
    sig = indata.flatten()
    vol = np.linalg.norm(sig) * 10
    
    buffer = np.roll(buffer, -len(sig))
    buffer[-len(sig):] = sig
    
    if vol > 5.0:
        res = aec.process_frame(buffer, vol)
        crest = res["crest_factor"]
        hp = res["hp_ratio"] * 100
        
        if res["is_impulse"]:
            print(f"⚡ [IMPULSE TAP DETECTED] Vol: {vol:.1f} | Crest: {crest:.2f} | High-Pass: {hp:.1f}%")
        elif vol > 15.0:
            print(f"🔊 [Music/Speech Energy Filtered] Vol: {vol:.1f} | Crest: {crest:.2f} | High-Pass: {hp:.1f}%")

try:
    with sd.InputStream(device=builtin_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
        while True:
            time.sleep(0.1)
except KeyboardInterrupt:
    aec.close()
    print("\n👋 Test completed.")
