import sounddevice as sd
import numpy as np
import time
import json
import os

from utils import find_builtin_mic, SAMPLE_RATE, WINDOW_SIZE

def extract_advanced_features(buffer_history, peak_idx):
    start_idx = max(0, peak_idx - 100)
    end_idx = min(len(buffer_history), peak_idx + 1000)
    transient = buffer_history[start_idx:end_idx]
    
    fft_vals = np.abs(np.fft.rfft(transient))
    freqs = np.fft.rfftfreq(len(transient), d=1.0/SAMPLE_RATE)
    
    rms = np.sqrt(np.mean(transient**2)) + 1e-6
    peak = np.max(np.abs(transient))
    crest_factor = peak / rms
    
    hp_energy = np.sum(fft_vals[freqs >= 2500]) + 1e-6
    total_fft_energy = np.sum(fft_vals) + 1e-6
    hp_ratio = hp_energy / total_fft_energy

    spectral_centroid = np.sum(freqs * fft_vals) / (total_fft_energy + 1e-6)

    pre_impact_start = max(0, peak_idx - 1440)
    pre_impact = buffer_history[pre_impact_start:peak_idx]
    pre_rms = np.sqrt(np.mean(pre_impact**2)) + 1e-6 if len(pre_impact) > 0 else 1e-6
    pre_surge_ratio = rms / pre_rms
    
    return [crest_factor, hp_ratio, spectral_centroid, pre_surge_ratio]

def main():
    print("==========================================================================")
    print("      MORSE - Advanced DSP Feature Calibration (Crest, HP, Surge)         ")
    print("==========================================================================")
    
    builtin_mic_id, dev_name = find_builtin_mic()
    print(f"🎙️ Target Hardware: [{builtin_mic_id}] {dev_name}")
    print("We will record 3 classes (20 events each) to find exact physical boundaries.")
    
    classes = [
        ("GENUINE TAPS", "Tap the palm rest normally 20 times"),
        ("WRIST RUBS / SLIDES", "Rub/slide your palm or wrist heavily on the metal 20 times"),
        ("HEAVY DESK THUDS", "Thump the desk hard (not the laptop) 20 times")
    ]
    
    all_data = {}
    buffer_history = np.zeros(WINDOW_SIZE)
    
    for class_name, desc in classes:
        input(f"\n👉 Press Enter to start recording {class_name} ({desc})...")
        
        records = []
        count = 0
        last_event = 0
        
        def callback(indata, frames, time_info, status):
            nonlocal count, last_event, buffer_history, records
            sig = indata.flatten()
            vol = np.linalg.norm(sig) * 10
            now = time.time()
            
            buffer_history = np.roll(buffer_history, -len(sig))
            buffer_history[-len(sig):] = sig
            
            if vol >= 2.0 and (now - last_event) > 0.4:
                peak_idx = np.argmax(np.abs(buffer_history))
                if True:
                    features = extract_advanced_features(buffer_history, peak_idx)
                    records.append(features)
                    count += 1
                    last_event = now
                    print(f"  [{class_name} #{count:02d}/20] Vol: {vol:5.1f} | Crest: {features[0]:.2f} | HP Ratio: {features[1]:.3f} | Centroid: {features[2]:.0f}Hz | Surge: {features[3]:.1f}")
                
        with sd.InputStream(device=builtin_mic_id, samplerate=SAMPLE_RATE, channels=1, callback=callback):
            while count < 20:
                time.sleep(0.1)
                
        all_data[class_name] = np.array(records)
        print(f"✅ 20 {class_name} successfully recorded!")
        
    print("\n=================================================================================================================")
    print("                                   ADVANCED FEATURE CALIBRATION RESULTS                                          ")
    print("=================================================================================================================")
    print(f"| Feature Name       | TAPS (Min - Max)       | RUBS (Min - Max)       | DESK (Min - Max)       | SEPARATION |")
    print(f"|--------------------|------------------------|------------------------|------------------------|------------|")
    
    feature_names = ["Crest Factor", "HP Ratio", "Centroid (Hz)", "Pre-Surge Ratio"]
    
    for idx, f_name in enumerate(feature_names):
        taps = all_data["GENUINE TAPS"][:, idx]
        rubs = all_data["WRIST RUBS / SLIDES"][:, idx]
        desk = all_data["HEAVY DESK THUDS"][:, idx]
        
        t_min, t_max = np.min(taps), np.max(taps)
        r_min, r_max = np.min(rubs), np.max(rubs)
        d_min, d_max = np.min(desk), np.max(desk)
        
        # Are Taps separated from Rubs/Desk?
        t_mean = np.mean(taps)
        r_mean = np.mean(rubs)
        d_mean = np.mean(desk)
        noise_mean = (r_mean + d_mean) / 2
        sep = abs(t_mean - noise_mean) / (np.std(taps) + np.std(rubs) + np.std(desk) + 1e-6)
        
        print(f"| {f_name:18s} | {t_min:6.2f} - {t_max:6.2f}      | {r_min:6.2f} - {r_max:6.2f}      | {d_min:6.2f} - {d_max:6.2f}      | {sep:5.2f}x     |")

if __name__ == "__main__":
    main()
