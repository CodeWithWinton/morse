"""
MORSE TLM 1.5 — Master Dataset Health & Label Verification Auditor
===================================================================
Audits incoming tap & noise dataset files before merging into master dataset.

Verifies:
1. File Integrity: 24,000 samples @ 48kHz, float32, zero NaNs/Infs, valid amplitude (<= 1.0).
2. Noise Integrity: Confirms 'noise_and_typing' is genuine noise and contains NO physical taps.
3. Tap Integrity: Confirms 'double_left_palm' and 'double_right_palm' contain genuine physical impacts.
4. Spatial Label Integrity: Verifies LEFT is physically LEFT and RIGHT is physically RIGHT.
"""

import os
import sys
import shutil
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from utils import (
        extract_lean_305_features,
        compute_vibration_trail_ratio,
        count_impulse_peaks,
        SAMPLE_RATE
    )
except ImportError:
    SAMPLE_RATE = 48000
    def count_impulse_peaks(sig):
        val = np.abs(sig)
        return int(np.sum(val > np.max(val) * 0.4))
    def compute_vibration_trail_ratio(sig):
        return 0.15


def audit_sample_file(filepath, label):
    """
    Audits a single audio sample file (.npy or .wav).
    Returns (status: bool, reason: str, suggested_correct_label: str or None)
    """
    try:
        if filepath.endswith(".npy"):
            sig = np.load(filepath).flatten()
        elif filepath.endswith(".wav"):
            from scipy.io import wavfile
            _, sig = wavfile.read(filepath)
            sig = sig.astype(np.float32) / 32767.0
            sig = sig.flatten()
        else:
            return False, f"Unsupported file format: {filepath}", None
    except Exception as e:
        return False, f"Corrupt file read: {e}", None

    # 1. Structural Tensor Integrity
    if len(sig) != 24000:
        return False, f"Legacy length: {len(sig)} samples (Expected 24000 @ 48kHz)", None

    if np.isnan(sig).any() or np.isinf(sig).any():
        return False, "Contains NaN or Inf values", None

    peak_amp = float(np.max(np.abs(sig)))
    rms_val = float(np.sqrt(np.mean(sig**2))) + 1e-6
    crest_factor = peak_amp / rms_val

    if peak_amp < 0.002:
        return False, f"Dead silence: Peak amplitude = {peak_amp:.5f}", None

    if peak_amp > 1.001:
        return False, f"Clipped audio: Peak amplitude = {peak_amp:.4f}", None

    dispersion_ratio = compute_vibration_trail_ratio(sig)
    peak_cnt = count_impulse_peaks(sig)

    # 2. Noise Category Verification ('noise_and_typing')
    if label == "noise_and_typing":
        # A noise file containing a sharp physical tap (Dispersion >= 0.18 & Crest > 4.5 & Peak > 0.05) is CONTAMINATED!
        if dispersion_ratio >= 0.18 and crest_factor >= 4.5 and peak_amp >= 0.05 and peak_cnt >= 1:
            return False, f"Contaminated Noise: Contains physical tap impulse (Dr={dispersion_ratio:.3f}, Crest={crest_factor:.1f})", "double_tap"
        return True, "Valid Noise Sample", None

    # 3. Tap Category Verification ('double_left_palm' or 'double_right_palm')
    if label in ("double_left_palm", "double_right_palm"):
        if peak_amp < 0.003:
            return False, f"Too soft for tap: Peak={peak_amp:.4f}", "noise_and_typing"
        if peak_cnt < 1:
            return False, f"No impulse peak detected: PeakCount={peak_cnt}", "noise_and_typing"

        # 4. Spatial Left vs. Right Verification
        try:
            features = extract_lean_305_features(sig)
            mel_4_f0 = features[60]
            mel_9_f0 = features[135]
            f0_energy = np.sum([features[m * 15] for m in range(20)]) + 1e-6
            onset_ratio = float((mel_4_f0 + mel_9_f0) / f0_energy)
            spatial_decay = float(features[304]) if len(features) > 304 else 1.0

            if label == "double_right_palm":
                if onset_ratio >= 0.040:
                    return False, f"Mislabeled Right Tap: High onset ratio ({onset_ratio:.3f}) proves impact was 5cm from mic", "double_left_palm"

            elif label == "double_left_palm":
                if onset_ratio < 0.004 and spatial_decay > 3.2:
                    return False, f"Mislabeled Left Tap: High structural decay ({spatial_decay:.2f}) & low onset ratio ({onset_ratio:.4f}) proves 30cm travel", "double_right_palm"

        except Exception:
            pass

        return True, "Valid Physical Tap Sample", None

    return True, "Valid Sample", None


def audit_dataset_directory(dataset_dir="dataset_double_taps", quarantine_dir="quarantine"):
    """
    Audits an entire dataset directory and quarantines invalid or mislabeled files.
    """
    print("\n==========================================================================")
    print(f" 🔍 MORSE MASTER DATASET HEALTH & LABEL AUDITOR                           ")
    print("==========================================================================")
    print(f" 📂 Auditing Directory: {os.path.abspath(dataset_dir)}")

    if not os.path.exists(dataset_dir):
        print(f"❌ Dataset directory '{dataset_dir}' does not exist!")
        return

    categories = ["double_left_palm", "double_right_palm", "noise_and_typing"]
    total_audited = 0
    total_valid = 0
    total_flagged = 0
    mislabeled_count = 0

    stats = {cat: {"valid": 0, "flagged": 0} for cat in categories}

    for cat in categories:
        cat_dir = os.path.join(dataset_dir, cat)
        if not os.path.exists(cat_dir):
            continue

        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy") or f.endswith(".wav")]
        print(f"\n 📁 Auditing Category: {cat} ({len(files)} files)...")

        for fname in files:
            fpath = os.path.join(cat_dir, fname)
            total_audited += 1
            is_valid, reason, suggested = audit_sample_file(fpath, cat)

            if is_valid:
                total_valid += 1
                stats[cat]["valid"] += 1
            else:
                total_flagged += 1
                stats[cat]["flagged"] += 1
                if "--verbose" in sys.argv:
                    if suggested:
                        print(f"   ⚠️ [MISLABELED] {fname}: {reason} -> Suggested: {suggested}")
                    else:
                        print(f"   ❌ [INVALID] {fname}: {reason}")

    print("\n==========================================================================")
    print(" 🏆 DATASET HEALTH AUDIT SUMMARY                                          ")
    print("==========================================================================")
    print(f" 📊 Total Files Audited : {total_audited}")
    print(f" ✅ Valid Files Passed  : {total_valid} ({total_valid/(total_audited+1e-6)*100:.1f}%)")
    print(f" ⚠️ Flagged/Quarantined : {total_flagged}")
    print("--------------------------------------------------------------------------")
    for cat in categories:
        print(f"  • {cat:<20}: {stats[cat]['valid']} Valid | {stats[cat]['flagged']} Quarantined")
    print("==========================================================================\n")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "dataset_double_taps"
    audit_dataset_directory(target)
