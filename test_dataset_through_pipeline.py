import os
import pickle
import numpy as np
from scipy.io import wavfile
from utils import extract_2d_spectrogram, DATASET_DIR, SAMPLE_RATE, WINDOW_SIZE

CATEGORIES = ["left_palm_rest", "right_palm_rest", "palm_resting", "typing", "noise", "desk_tap"]
MODEL_PATH = "model_2d.pkl"

def main():
    if not os.path.exists(MODEL_PATH):
        print("❌ model_2d.pkl not found!")
        return

    with open(MODEL_PATH, "rb") as f:
        model_data = pickle.load(f)

    clf = model_data["model"]
    categories = model_data["categories"]

    print("==========================================================================")
    print("   MORSE - Full Dataset Evaluation Through Calibrated Pipeline           ")
    print("==========================================================================")

    results = {}

    for cat in CATEGORIES:
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue

        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy") or f.endswith(".wav")]
        
        total_samples = len(files)
        dsp_passed = 0
        ml_valid = 0
        detected_left = 0
        detected_right = 0
        blocked_other = 0

        for f_name in files:
            f_path = os.path.join(cat_dir, f_name)
            if f_name.endswith(".npy"):
                sig = np.load(f_path)
            else:
                sr, sig = wavfile.read(f_path)
                sig = sig.astype(np.float32) / 32768.0

            sig = sig.flatten()
            vol = np.linalg.norm(sig) * 10

            # Buffer history padding/slicing
            if len(sig) < WINDOW_SIZE:
                buffer_history = np.pad(sig, (0, WINDOW_SIZE - len(sig)))
            else:
                buffer_history = sig[-WINDOW_SIZE:]

            peak_idx = np.argmax(np.abs(buffer_history))
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

            pre_impact_start = max(0, peak_idx - 1440)
            pre_impact = buffer_history[pre_impact_start:peak_idx]
            pre_rms = np.sqrt(np.mean(pre_impact**2)) + 1e-6 if len(pre_impact) > 0 else 1e-6
            pre_surge_ratio = rms / pre_rms

            min_pre_surge = 1.8 if vol < 5.0 else 2.1

            # Stage 1 DSP Candidate Filter
            is_dsp_candidate = (vol >= 3.5) and (vol <= 110.0) and (crest_factor >= 1.60) and (hp_ratio >= 0.05 or pre_surge_ratio >= min_pre_surge)

            if is_dsp_candidate:
                dsp_passed += 1
                features = extract_2d_spectrogram(buffer_history)
                pred_idx = clf.predict([features])[0]
                probs = clf.predict_proba([features])[0]
                confidence = probs[pred_idx] * 100
                predicted_label = categories[pred_idx]

                bass_ratio, hp_feat, centroid_feat, rolloff_feat, zcr_feat, flatness_feat, pitch_feat = features[-7:]
                pitch_hz = pitch_feat * 10000.0
                centroid_hz = centroid_feat * 10000.0

                # Empirical Spatial Side Determination (ML Model Primary + Damped Centroid Guardrail)
                is_physically_right = (predicted_label == "right_palm_rest") or (hp_feat < 0.08 and centroid_hz < 2000.0)
                detected_side = "right" if is_physically_right else "left"

                is_valid_tap = predicted_label in ["left_palm_rest", "right_palm_rest", "tap"]

                if is_valid_tap:
                    ml_valid += 1
                    if detected_side == "left":
                        detected_left += 1
                    else:
                        detected_right += 1
                else:
                    blocked_other += 1

        results[cat] = {
            "total": total_samples,
            "dsp_passed": dsp_passed,
            "ml_valid": ml_valid,
            "left": detected_left,
            "right": detected_right,
            "blocked": blocked_other
        }

    print("\n=========================================================================================================")
    print("                              STAGE 1 DSP + STAGE 2 ML PIPELINE RESULTS                                  ")
    print("=========================================================================================================")
    print(f"| Category         | Total Samples | Stage 1 DSP Passed | Valid Taps | Detected LEFT | Detected RIGHT | Spatial Accuracy |")
    print(f"|------------------|---------------|--------------------|------------|---------------|----------------|------------------|")

    for cat, res in results.items():
        total = res["total"]
        if total == 0:
            continue
        dsp_p = res["dsp_passed"]
        val = res["ml_valid"]
        l_det = res["left"]
        r_det = res["right"]
        
        if cat == "left_palm_rest":
            accuracy_str = f"{(l_det / total)*100:.1f}% LEFT"
        elif cat == "right_palm_rest":
            accuracy_str = f"{(r_det / total)*100:.1f}% RIGHT"
        else:
            rejected = total - val
            accuracy_str = f"{(rejected / total)*100:.1f}% REJECTED"
        
        print(f"| {cat.upper():16s} | {total:13d} | {dsp_p:18d} | {val:10d} | {l_det:13d} | {r_det:14d} | {accuracy_str:16s} |")

if __name__ == "__main__":
    main()
