#!/usr/bin/env python3
"""
Dual-Mic Spatial Test
======================
Records from BOTH the built-in mic AND external mic simultaneously.
Compares volume/timing between the two to test spatial discrimination.

Place external mic on the RIGHT side of your laptop.
Built-in mic is on the LEFT side.

LEFT tap  → louder on built-in (device 3), quieter on external (device 1)
RIGHT tap → quieter on built-in (device 3), louder on external (device 1)
"""

import sounddevice as sd
import numpy as np
import time
import threading

SAMPLE_RATE = 48000
BLOCK_SIZE = 1024

BUILTIN_MIC = 3   # MacBook Air Microphone (LEFT side)
EXTERNAL_MIC = 1  # External Microphone (RIGHT side)

# Shared state
builtin_volume = 0.0
external_volume = 0.0
builtin_peak_time = 0.0
external_peak_time = 0.0

def builtin_callback(indata, frames, time_info, status):
    global builtin_volume, builtin_peak_time
    vol = np.linalg.norm(indata.flatten()) * 10
    if vol > builtin_volume:
        builtin_volume = vol
        builtin_peak_time = time.time()

def external_callback(indata, frames, time_info, status):
    global external_volume, external_peak_time
    vol = np.linalg.norm(indata.flatten()) * 10
    if vol > external_volume:
        external_volume = vol
        external_peak_time = time.time()

def main():
    global builtin_volume, external_volume, builtin_peak_time, external_peak_time

    print("="*60)
    print("  MORSE - Dual-Mic Spatial Discrimination Test")
    print("="*60)
    print(f"\n🎙️  Built-in Mic (LEFT):  Device [{BUILTIN_MIC}]")
    print(f"🎙️  External Mic (RIGHT): Device [{EXTERNAL_MIC}]")
    print("\n📍 Place external mic on the RIGHT side of your laptop.")
    print("   Then tap LEFT palm rest and RIGHT palm rest separately.")
    print("\nExpected:")
    print("   LEFT tap  → Built-in LOUD, External QUIET")
    print("   RIGHT tap → Built-in QUIET, External LOUD")
    print("\nPress Ctrl+C to stop.\n")

    try:
        stream_builtin = sd.InputStream(
            device=BUILTIN_MIC, samplerate=SAMPLE_RATE,
            channels=1, blocksize=BLOCK_SIZE, callback=builtin_callback
        )
        stream_external = sd.InputStream(
            device=EXTERNAL_MIC, samplerate=SAMPLE_RATE,
            channels=1, blocksize=BLOCK_SIZE, callback=external_callback
        )

        stream_builtin.start()
        stream_external.start()

        tap_count = 0
        THRESHOLD = 3.0

        while True:
            time.sleep(0.02)  # 50Hz polling

            # Check if either mic detected a tap
            if builtin_volume >= THRESHOLD or external_volume >= THRESHOLD:
                tap_count += 1

                # Wait 50ms for both mics to register the peak
                time.sleep(0.05)

                bv = builtin_volume
                ev = external_volume

                # Determine spatial side
                if bv > 0 and ev > 0:
                    ratio = bv / (ev + 1e-6)
                    if ratio > 1.5:
                        side = "⬅️  LEFT (built-in louder)"
                    elif ratio < 0.67:
                        side = "➡️  RIGHT (external louder)"
                    else:
                        side = "🔘 CENTER (similar volume)"
                elif bv > ev:
                    side = "⬅️  LEFT"
                    ratio = bv / (ev + 1e-6)
                else:
                    side = "➡️  RIGHT"
                    ratio = bv / (ev + 1e-6)

                # Time difference (TDOA)
                tdoa_ms = (external_peak_time - builtin_peak_time) * 1000

                print(f"  Tap #{tap_count:02d} | Built-in: {bv:5.1f} | External: {ev:5.1f} | Ratio: {ratio:.2f} | TDOA: {tdoa_ms:+.1f}ms | {side}")

                # Reset for next tap
                builtin_volume = 0.0
                external_volume = 0.0
                time.sleep(0.3)  # Debounce

    except KeyboardInterrupt:
        print("\n\n👋 Stopped dual-mic test.")
        stream_builtin.stop()
        stream_external.stop()

if __name__ == "__main__":
    main()
