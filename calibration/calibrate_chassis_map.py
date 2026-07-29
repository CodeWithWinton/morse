#!/usr/bin/env python3
"""
Morse Chassis Acoustic Mapping Tool
====================================
Scientific calibration: map acoustic signatures across the MacBook chassis grid.

Instead of random taps, this tool:
1. Defines a precise 3x3 grid of tap locations
2. Records 10 taps at each location
3. Analyzes distance-to-mic propagation patterns
4. Builds an acoustic fingerprint database
5. Calculates optimal detection thresholds per zone

Usage:
    python3 calibrate_chassis_map.py
"""

import sounddevice as sd
import numpy as np
import time
import json
from utils import find_builtin_mic, extract_2d_spectrogram, SAMPLE_RATE, WINDOW_SIZE

# Define 3x3 grid zones (in cm from left edge, relative to mic position)
# MacBook Air 13": ~30cm wide, mic at ~3cm from left edge
CHASSIS_GRID = {
    "LEFT_FRONT": {"x": 5, "y": 15, "distance_to_mic": 5},
    "LEFT_CENTER": {"x": 5, "y": 10, "distance_to_mic": 3},
    "LEFT_BACK": {"x": 5, "y": 5, "distance_to_mic": 5},

    "CENTER_FRONT": {"x": 15, "y": 15, "distance_to_mic": 15},
    "CENTER_CENTER": {"x": 15, "y": 10, "distance_to_mic": 12},
    "CENTER_BACK": {"x": 15, "y": 5, "distance_to_mic": 15},

    "RIGHT_FRONT": {"x": 25, "y": 15, "distance_to_mic": 27},
    "RIGHT_CENTER": {"x": 25, "y": 10, "distance_to_mic": 25},
    "RIGHT_BACK": {"x": 25, "y": 5, "distance_to_mic": 27},
}

def record_tap_sample(duration=0.5):
    """Record a single tap sample."""
    samples = []

    def callback(indata, frames, time_info, status):
        samples.append(indata.copy())

    with sd.InputStream(device=builtin_device_id, samplerate=SAMPLE_RATE,
                        channels=1, callback=callback):
        time.sleep(duration)

    return np.concatenate(samples).flatten()

def analyze_tap_signature(signal):
    """Extract acoustic signature from tap signal."""
    # Volume
    volume = np.linalg.norm(signal) * 10

    # Peak amplitude
    peak = np.max(np.abs(signal))

    # RMS
    rms = np.sqrt(np.mean(signal**2))

    # Crest factor
    crest_factor = peak / (rms + 1e-6)

    # FFT analysis
    fft_vals = np.abs(np.fft.rfft(signal[-WINDOW_SIZE:]))
    freqs = np.fft.rfftfreq(WINDOW_SIZE, d=1.0/SAMPLE_RATE)

    # Bass energy (120-600 Hz)
    bass_energy = np.sum(fft_vals[(freqs >= 120) & (freqs <= 600)])

    # High-freq energy (> 2500 Hz)
    high_energy = np.sum(fft_vals[freqs > 2500])

    # Spectral centroid
    spectral_centroid = np.sum(freqs * fft_vals) / (np.sum(fft_vals) + 1e-6)

    # 2D spectrogram features
    spec_features = extract_2d_spectrogram(signal[-WINDOW_SIZE:])

    return {
        "volume": float(volume),
        "peak": float(peak),
        "rms": float(rms),
        "crest_factor": float(crest_factor),
        "bass_energy": float(bass_energy),
        "high_energy": float(high_energy),
        "spectral_centroid": float(spectral_centroid),
        "spectrogram_mean": float(np.mean(spec_features)),
        "spectrogram_std": float(np.std(spec_features)),
    }

def calibrate_zone(zone_name, zone_info, num_taps=10):
    """Calibrate a specific chassis zone."""
    print(f"\n{'='*60}")
    print(f"Zone: {zone_name}")
    print(f"Location: {zone_info['x']}cm from left, {zone_info['y']}cm from front")
    print(f"Distance to mic: {zone_info['distance_to_mic']}cm")
    print(f"{'='*60}")

    print(f"\n📍 Place your finger at the marked location.")
    print(f"   Tap {num_taps} times with CONSISTENT medium pressure.")
    print(f"   Wait for countdown between taps.\n")

    input("Press ENTER when ready to start...")

    signatures = []

    for i in range(num_taps):
        print(f"\nTap {i+1}/{num_taps} in...")
        for countdown in [3, 2, 1]:
            print(f"  {countdown}...")
            time.sleep(1)
        print("  👆 TAP NOW!")

        # Record tap
        signal = record_tap_sample(duration=0.5)
        signature = analyze_tap_signature(signal)
        signatures.append(signature)

        print(f"     ✓ Recorded (Vol: {signature['volume']:.1f}, Centroid: {signature['spectral_centroid']:.0f} Hz)")

        time.sleep(1)  # Pause between taps

    # Aggregate statistics
    aggregated = {
        "zone": zone_name,
        "distance_to_mic_cm": zone_info['distance_to_mic'],
        "num_samples": len(signatures),
        "signatures": signatures,
        "statistics": {
            "volume_mean": np.mean([s["volume"] for s in signatures]),
            "volume_std": np.std([s["volume"] for s in signatures]),
            "volume_min": np.min([s["volume"] for s in signatures]),
            "volume_max": np.max([s["volume"] for s in signatures]),
            "centroid_mean": np.mean([s["spectral_centroid"] for s in signatures]),
            "centroid_std": np.std([s["spectral_centroid"] for s in signatures]),
            "crest_mean": np.mean([s["crest_factor"] for s in signatures]),
            "bass_mean": np.mean([s["bass_energy"] for s in signatures]),
            "high_mean": np.mean([s["high_energy"] for s in signatures]),
        }
    }

    print(f"\n✅ Zone {zone_name} calibration complete!")
    print(f"   Volume: {aggregated['statistics']['volume_mean']:.1f} ± {aggregated['statistics']['volume_std']:.1f}")
    print(f"   Centroid: {aggregated['statistics']['centroid_mean']:.0f} ± {aggregated['statistics']['centroid_std']:.0f} Hz")

    return aggregated

def main():
    global builtin_device_id

    builtin_device_id, dev_name = find_builtin_mic()
    print(f"🎙️  Target Hardware: [{builtin_device_id}] {dev_name}\n")

    print("="*60)
    print("  MORSE - Chassis Acoustic Mapping Calibration")
    print("="*60)
    print("\nThis tool will systematically map acoustic signatures across")
    print("your MacBook chassis in a 3x3 grid (9 zones total).")
    print(f"\nYou'll tap each zone {10} times with consistent pressure.")
    print("The tool will analyze propagation patterns and build an")
    print("acoustic fingerprint database.\n")

    print("⚠️  IMPORTANT:")
    print("   • Find a quiet environment")
    print("   • Use the same finger (index) for all taps")
    print("   • Tap with MEDIUM pressure (not soft, not hard)")
    print("   • This will take ~15-20 minutes total\n")

    input("Press ENTER to start calibration...")

    # Calibrate each zone
    results = {}

    for zone_name, zone_info in CHASSIS_GRID.items():
        results[zone_name] = calibrate_zone(zone_name, zone_info, num_taps=10)

        # Save incremental results
        with open("chassis_acoustic_map.json", "w") as f:
            json.dump(results, f, indent=2)

    # Final analysis
    print("\n" + "="*60)
    print("  CALIBRATION COMPLETE - Acoustic Map Summary")
    print("="*60)

    print("\n📊 Volume vs Distance Analysis:")
    for zone_name, data in results.items():
        stats = data["statistics"]
        distance = data["distance_to_mic_cm"]
        print(f"  {zone_name:20s} | {distance:2d}cm | Vol: {stats['volume_mean']:5.1f} ± {stats['volume_std']:4.1f}")

    # Distance-based damping analysis
    print("\n📉 Propagation Damping Factor:")
    left_vol = results["LEFT_CENTER"]["statistics"]["volume_mean"]
    right_vol = results["RIGHT_CENTER"]["statistics"]["volume_mean"]
    damping_factor = right_vol / left_vol
    print(f"   Right/Left Ratio: {damping_factor:.2f}x")
    print(f"   30cm Aluminum Damping: {(1 - damping_factor) * 100:.1f}% energy loss")

    # Optimal thresholds
    print("\n🎯 Recommended Detection Thresholds:")
    all_volumes = [data["statistics"]["volume_mean"] for data in results.values()]
    global_min = np.min(all_volumes)
    global_mean = np.mean(all_volumes)

    print(f"   Global minimum volume: {global_min:.1f}")
    print(f"   Global mean volume: {global_mean:.1f}")
    print(f"   Suggested threshold: {global_min * 0.8:.1f} (80% of min)")

    print(f"\n💾 Results saved to: chassis_acoustic_map.json")
    print(f"\n✅ Use this data to set zone-specific thresholds in smart_detector.py\n")

if __name__ == "__main__":
    main()
