import sounddevice as sd
import numpy as np
import time
import sys
import json
import os

from utils import find_builtin_mic, extract_2d_spectrogram, SAMPLE_RATE, WINDOW_SIZE

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "normal"
    out_file = f"calib_{mode}.json"
    
    print("==========================================================================")
    print(f"     MORSE - 60/60 Multi-Factor Calibration Suite [{mode.upper()} MODE]     ")
    print("==========================================================================")
    
    builtin_mic_id, dev_name = find_builtin_mic()
    print(f"🎙️ Target Hardware: [{builtin_mic_id}] {dev_name}")
    print(f"Mode: {mode.upper()} | Output File: {out_file}")
    print(f"This tool will record 60 Left and 60 Right [{mode.upper()}] taps.")
    
    input("👉 Press Enter to start recording 60 LEFT Palm Rest Taps...")
    
    left_features = []
    right_features = []
    
    buffer_history = np.zeros(WINDOW_SIZE)
    
    print("\n📍 Recording 60 LEFT Palm Rest Taps (Tap your left palm rest 60 times naturally)...")
    count = 0
    t0 = time.time()
    
    def record_taps(target_list, label_str, target_count=60):
        nonlocal buffer_history
        count = 0
        last_tap = 0
        
        def callback(indata, frames, time_info, status):
            nonlocal count, last_tap, buffer_history
            sig = indata.flatten()
            vol = np.linalg.norm(sig) * 10
            now = time.time()
            
            buffer_history = np.roll(buffer_history, -len(sig))
            buffer_history[-len(sig):] = sig
            
            if vol >= 3.2 and (now - last_tap) > 0.35:
                feat = extract_2d_spectrogram(buffer_history)
                # The 7 physical features appended at end of feat array
                phys = feat[-7:]
                target_list.append(phys)
                count += 1
                last_tap = now
                print(f"  [{label_str} Tap #{count:02d}/60] Vol: {vol:5.1f} | Bass: {phys[0]:.3f} | HP: {phys[1]:.3f} | Centroid: {phys[2]*10000:.0f}Hz | Pitch: {phys[6]*10000:.0f}Hz")
                
        with sd.InputStream(device=builtin_mic_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while count < target_count:
                time.sleep(0.1)
                
    record_taps(left_features, "LEFT", 60)
    print("\n✅ 60 LEFT Palm Rest Taps successfully recorded!\n")
    
    input("👉 Press Enter to start recording 60 RIGHT Palm Rest Taps...")
    record_taps(right_features, "RIGHT", 60)
    print("\n✅ 60 RIGHT Palm Rest Taps successfully recorded!\n")
    
    left_arr = np.array(left_features)
    right_arr = np.array(right_features)
    
    feature_names = ["Bass Ratio", "HP Ratio", "Centroid (Hz)", "Rolloff (Hz)", "ZCR", "Flatness", "Pitch (Hz)"]
    scales = [1.0, 1.0, 10000.0, 10000.0, 1.0, 1.0, 10000.0]
    
    print("\n=========================================================================================================")
    print("                              EMPIRICAL 60/60 FEATURE DISTRIBUTION RESULTS                              ")
    print("=========================================================================================================")
    print(f"| Feature Name          | LEFT Mean (Min - Max)              | RIGHT Mean (Min - Max)             | Separation |")
    print(f"|-----------------------|------------------------------------|------------------------------------|------------|")
    
    calib_summary = {}
    for idx, f_name in enumerate(feature_names):
        l_vals = left_arr[:, idx] * scales[idx]
        r_vals = right_arr[:, idx] * scales[idx]
        
        l_mean, l_min, l_max = np.mean(l_vals), np.min(l_vals), np.max(l_vals)
        r_mean, r_min, r_max = np.mean(r_vals), np.min(r_vals), np.max(r_vals)
        
        sep_ratio = abs(l_mean - r_mean) / (np.std(l_vals) + np.std(r_vals) + 1e-6)
        
        print(f"| {f_name:21s} | {l_mean:7.2f} ({l_min:6.2f} - {l_max:6.2f})   | {r_mean:7.2f} ({r_min:6.2f} - {r_max:6.2f})   | {sep_ratio:5.2f}x      |")
        
        calib_summary[f_name] = {
            "left": {"mean": float(l_mean), "min": float(l_min), "max": float(l_max)},
            "right": {"mean": float(r_mean), "min": float(r_min), "max": float(r_max)}
        }
        
    with open(out_file, "w") as f:
        json.dump(calib_summary, f, indent=2)
        
    print("=========================================================================================================")
    print(f"✅ Calibration matrix saved to '{out_file}'!")

if __name__ == "__main__":
    main()
