import sounddevice as sd
import numpy as np
import time
import sys

from utils import compute_vibration_trail_ratio, find_builtin_mic, SAMPLE_RATE

# 350ms Audio Window
DOUBLE_TAP_WINDOW = 16800

def main():
    device_id, dev_name = find_builtin_mic()
    print("==========================================================================")
    print("      MORSE - Mechanical Unibody Vibration Trail Decay Diagnostic        ")
    print("==========================================================================")
    print(f"🎙️ Target Hardware: [{device_id}] {dev_name}")
    print("🔬 Measuring exponential ring-down vibration trail (15ms - 35ms after peak impact)")
    print("👉 Try Double-Tapping Palm Rest vs. Snapping Earphone Lid vs. Pen Clicks!\n")

    buffer_history = np.zeros(DOUBLE_TAP_WINDOW, dtype=np.float32)

    def callback(indata, frames, time_info, status):
        nonlocal buffer_history
        sig = indata.flatten()
        volume = np.linalg.norm(sig) * 10

        buffer_history = np.roll(buffer_history, -len(sig))
        buffer_history[-len(sig):] = sig

        if volume > 3.0:
            trail_ratio = compute_vibration_trail_ratio(buffer_history)
            
            if trail_ratio >= 0.15:
                tag = "✅ CHASSIS TAP (Solid Aluminum Mechanical Wave)"
            else:
                tag = "❌ AIR SNAP / LID CLICK (Sharp 1ms Spike, Zero Surrounding Energy)"
                
            print(f"🔊 Vol: {volume:4.1f} | 🌊 Dispersion Ratio: {trail_ratio:.3f} | {tag}")
            time.sleep(0.3)

    try:
        with sd.InputStream(device=builtin_device_id if 'builtin_device_id' in locals() else device_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while True:
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\n👋 Stopping Vibration Trail Diagnostic cleanly...")

if __name__ == "__main__":
    main()
