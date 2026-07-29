"""
MORSE TLM 1.5 — Master Dataset Health & Tensor Auditor
======================================================
Audits incoming tap & noise dataset files before merging into master dataset.

Auto-Fix Features:
1. Auto-Pads 16,800-sample legacy clips to 24,000 samples @ 48kHz.
2. Auto-Normalizes clipped floating-point audio signals (> 1.0).
3. Verifies zero NaNs, zero Infs, and non-silent audio.
"""

import os
import sys
import numpy as np

SAMPLE_RATE = 48000
TARGET_SAMPLES = 24000  # 500ms @ 48kHz


def audit_sample_file(filepath, label, auto_fix=True):
    """
    Audits a single audio sample file (.npy or .wav) with auto-repair.
    Returns (status: bool, reason: str, modified: bool)
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
            return False, f"Unsupported file format: {filepath}", False
    except Exception as e:
        return False, f"Corrupt file read: {e}", False

    modified = False

    # 1. NaN / Inf Check
    if np.isnan(sig).any() or np.isinf(sig).any():
        return False, "Contains NaN or Inf values", False

    # 2. Dead Silence Check
    peak_amp = float(np.max(np.abs(sig)))
    if peak_amp < 0.0001:
        return False, f"Dead silence: Peak = {peak_amp:.6f}", False

    # 3. Auto-Normalize Clipped / Over-Scaled Floating-Point Audio
    if peak_amp > 1.0:
        sig = sig / peak_amp
        modified = True

    # 4. Auto-Pad 16,800 Legacy 350ms Window Samples to 24,000 Samples (500ms)
    if len(sig) < TARGET_SAMPLES:
        pad_len = TARGET_SAMPLES - len(sig)
        sig = np.pad(sig, (0, pad_len), mode="constant")
        modified = True
    elif len(sig) > TARGET_SAMPLES:
        sig = sig[:TARGET_SAMPLES]
        modified = True

    # Save repaired file back if modified
    if modified and auto_fix and filepath.endswith(".npy"):
        try:
            np.save(filepath, sig.astype(np.float32))
        except Exception:
            pass

    return True, "Valid Physical Sample", modified


def audit_dataset_directory(dataset_dir="dataset_double_taps", auto_fix=True):
    """
    Audits an entire dataset directory and auto-repairs tensor scaling/padding.
    """
    print("\n==========================================================================")
    print(f" 🔍 MORSE MASTER DATASET HEALTH & TENSOR AUDITOR                          ")
    print("==========================================================================")
    print(f" 📂 Auditing Directory: {os.path.abspath(dataset_dir)}")

    if not os.path.exists(dataset_dir):
        print(f"❌ Dataset directory '{dataset_dir}' does not exist!")
        return

    categories = ["double_left_palm", "double_right_palm", "noise_and_typing"]
    total_audited = 0
    total_valid = 0
    total_repaired = 0
    total_corrupt = 0

    stats = {cat: {"valid": 0, "repaired": 0, "corrupt": 0} for cat in categories}

    for cat in categories:
        cat_dir = os.path.join(dataset_dir, cat)
        if not os.path.exists(cat_dir):
            continue

        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy") or f.endswith(".wav")]
        print(f" 📁 Auditing Category: {cat} ({len(files)} files)...")

        for fname in files:
            fpath = os.path.join(cat_dir, fname)
            total_audited += 1
            is_valid, reason, was_repaired = audit_sample_file(fpath, cat, auto_fix=auto_fix)

            if is_valid:
                total_valid += 1
                if was_repaired:
                    total_repaired += 1
                    stats[cat]["repaired"] += 1
                else:
                    stats[cat]["valid"] += 1
            else:
                total_corrupt += 1
                stats[cat]["corrupt"] += 1

    print("\n==========================================================================")
    print(" 🏆 DATASET HEALTH AUDIT SUMMARY                                          ")
    print("==========================================================================")
    print(f" 📊 Total Files Audited : {total_audited}")
    print(f" ✅ Valid Files Passed  : {total_valid} ({total_valid/(total_audited+1e-6)*100:.1f}%)")
    print(f" 🛠️ Auto-Repaired       : {total_repaired} (Padded/Normalized)")
    print(f" ❌ Unrepairable Corrupt: {total_corrupt}")
    print("--------------------------------------------------------------------------")
    for cat in categories:
        print(f"  • {cat:<20}: {stats[cat]['valid'] + stats[cat]['repaired']} Valid ({stats[cat]['repaired']} Repaired) | {stats[cat]['corrupt']} Corrupt")
    print("==========================================================================\n")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "dataset_double_taps"
    audit_dataset_directory(target)
