import os
import numpy as np
from dsp_filter import classify_audio_frame

DATASET_DIR = "dataset"
CATEGORIES = ["tap", "typing", "noise"]

def run_test_suite():
    print("==========================================================================")
    print("           MORSE - DSP Filter Offline Test Suite                          ")
    print("==========================================================================\n")
    
    total_samples = 0
    correct_predictions = 0
    results = {}
    
    for cat in CATEGORIES:
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
            
        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy")]
        cat_total = len(files)
        cat_correct = 0
        
        ratios = []
        crest_factors = []
        
        for f in files:
            sig = np.load(os.path.join(cat_dir, f))
            is_tap, ratio, crest_factor, vol = classify_audio_frame(sig)
            
            ratios.append(ratio)
            crest_factors.append(crest_factor)
            
            # Ground truth expectation:
            # "tap" -> should be True
            # "typing" & "noise" -> should be False
            expected = (cat == "tap")
            if is_tap == expected:
                cat_correct += 1
                correct_predictions += 1
            total_samples += 1
            
        acc = (cat_correct / cat_total) * 100 if cat_total > 0 else 0
        results[cat] = {
            "total": cat_total,
            "correct": cat_correct,
            "accuracy": acc,
            "avg_ratio": np.mean(ratios) if ratios else 0,
            "avg_crest": np.mean(crest_factors) if crest_factors else 0
        }
        
    print(f"{'Category':<15} | {'Samples':<10} | {'Correct':<10} | {'Accuracy':<10} | {'Avg Ratio':<10} | {'Avg Crest':<10}")
    print("-" * 75)
    
    for cat, res in results.items():
        print(f"{cat:<15} | {res['total']:<10} | {res['correct']:<10} | {res['accuracy']:>8.1f}% | {res['avg_ratio']:>9.2f} | {res['avg_crest']:>9.2f}")
        
    overall_acc = (correct_predictions / total_samples) * 100 if total_samples > 0 else 0
    print("\n" + "=" * 75)
    print(f"📊 OVERALL DSP SUITE ACCURACY: {overall_acc:.1f}% ({correct_predictions}/{total_samples} samples)")
    print("=" * 75 + "\n")

if __name__ == "__main__":
    run_test_suite()
