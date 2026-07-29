"""
MORSE TLM 1.5 — Universal Hugging Face Dataset Sync Suite
=========================================================
Supports:
1. PULL: Download latest master dataset (HDF5 + raw .npy) from Hugging Face.
2. PUSH / CONTRIBUTE: Push local tap & noise contributions with rich metadata
   (laptop model, sample counts, audit %, contributor info, data bias summary).
"""

import os
import sys
import json
import platform
import subprocess
import datetime
import numpy as np

HF_DATASET_REPO = "CodeWithWinton/macbook-unibody-acoustic-tap-dataset"
HF_MODEL_REPO = "CodeWithWinton/morse-tlm1_5-acoustic-gesture-model"

try:
    from huggingface_hub import HfApi, hf_hub_download, snapshot_download
except ImportError:
    print("⏳ Installing huggingface_hub dependency...")
    subprocess.run([sys.executable, "-m", "pip", "install", "huggingface_hub"], check=True)
    from huggingface_hub import HfApi, hf_hub_download, snapshot_download


def detect_laptop_model():
    """Auto-detect laptop manufacturer and model name across macOS, Windows, and Linux."""
    system = platform.system()
    try:
        if system == "Darwin":
            # macOS: system_profiler gives exact model (e.g. "MacBook Air (M1, 2020)")
            res = subprocess.run(
                ["system_profiler", "SPHardwareDataType"],
                capture_output=True, text=True, timeout=3
            )
            for line in res.stdout.split("\n"):
                if "Model Name" in line:
                    return line.split(":")[1].strip()
            return f"Apple {platform.machine()}"

        elif system == "Windows":
            # Windows: WMIC gives manufacturer + model (e.g. "Dell XPS 15 9520")
            res = subprocess.run(
                ["wmic", "csproduct", "get", "name,vendor", "/format:list"],
                capture_output=True, text=True, timeout=3
            )
            vendor = model = ""
            for line in res.stdout.strip().split("\n"):
                if line.startswith("Name="):
                    model = line.split("=", 1)[1].strip()
                elif line.startswith("Vendor="):
                    vendor = line.split("=", 1)[1].strip()
            return f"{vendor} {model}".strip() or f"Windows {platform.machine()}"

        elif system == "Linux":
            # Linux: /sys/devices/virtual/dmi/id/
            vendor = model = ""
            try:
                with open("/sys/devices/virtual/dmi/id/sys_vendor") as f:
                    vendor = f.read().strip()
                with open("/sys/devices/virtual/dmi/id/product_name") as f:
                    model = f.read().strip()
            except FileNotFoundError:
                pass
            return f"{vendor} {model}".strip() or f"Linux {platform.machine()}"

    except Exception:
        pass
    return f"{system} {platform.machine()}"


def count_dataset_samples(dataset_dir="dataset_double_taps"):
    """Count .npy samples per category in the dataset directory."""
    categories = ["double_left_palm", "double_right_palm", "noise_and_typing"]
    counts = {}
    total = 0
    for cat in categories:
        cat_dir = os.path.join(dataset_dir, cat)
        if os.path.exists(cat_dir):
            n = len([f for f in os.listdir(cat_dir) if f.endswith(".npy")])
        else:
            n = 0
        counts[cat] = n
        total += n
    counts["total"] = total
    return counts


def run_audit(dataset_dir="dataset_double_taps"):
    """Run the audit script and return pass/fail counts."""
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    try:
        from data_tools.audit_incoming_data import audit_sample_file
    except ImportError:
        return None, None

    categories = ["double_left_palm", "double_right_palm", "noise_and_typing"]
    total = 0
    passed = 0
    for cat in categories:
        cat_dir = os.path.join(dataset_dir, cat)
        if not os.path.exists(cat_dir):
            continue
        for f in os.listdir(cat_dir):
            if f.endswith(".npy"):
                total += 1
                ok, _, _ = audit_sample_file(os.path.join(cat_dir, f), cat)
                if ok:
                    passed += 1
    return passed, total


def build_contribution_manifest(dataset_dir, contributor_name, laptop_model, counts, audit_passed, audit_total):
    """Build a rich JSON manifest describing this contribution."""
    bias_summary = []
    if counts.get("double_left_palm", 0) > counts.get("double_right_palm", 0) * 1.3:
        bias_summary.append("Left-heavy: significantly more left tap samples than right")
    elif counts.get("double_right_palm", 0) > counts.get("double_left_palm", 0) * 1.3:
        bias_summary.append("Right-heavy: significantly more right tap samples than left")
    else:
        bias_summary.append("Balanced: roughly equal left and right tap samples")

    noise_ratio = counts.get("noise_and_typing", 0) / max(counts.get("total", 1), 1)
    if noise_ratio > 0.6:
        bias_summary.append("Noise-dominant: >60% of samples are noise/typing")
    elif noise_ratio < 0.3:
        bias_summary.append("Tap-dominant: <30% noise samples, may need more noise data")

    manifest = {
        "contributor": contributor_name,
        "laptop_model": laptop_model,
        "platform": f"{platform.system()} {platform.release()} ({platform.machine()})",
        "python_version": platform.python_version(),
        "timestamp_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "sample_counts": {
            "double_left_palm": counts.get("double_left_palm", 0),
            "double_right_palm": counts.get("double_right_palm", 0),
            "noise_and_typing": counts.get("noise_and_typing", 0),
            "total": counts.get("total", 0),
        },
        "audit": {
            "passed": audit_passed,
            "total": audit_total,
            "pass_rate": f"{audit_passed / max(audit_total, 1) * 100:.1f}%",
        },
        "data_bias": bias_summary,
        "sample_rate_hz": 48000,
        "window_ms": 500,
        "samples_per_file": 24000,
        "file_format": "numpy .npy (float32)",
    }
    return manifest


def build_commit_message(contributor_name, laptop_model, counts, audit_passed, audit_total):
    """Build a rich, descriptive commit message for the HF push."""
    audit_pct = f"{audit_passed / max(audit_total, 1) * 100:.1f}%"
    msg = (
        f"contrib({contributor_name}): {counts['total']} samples from {laptop_model}\n\n"
        f"Contributor : {contributor_name}\n"
        f"Laptop Model: {laptop_model}\n"
        f"Platform    : {platform.system()} {platform.release()} ({platform.machine()})\n"
        f"Timestamp   : {datetime.datetime.utcnow().isoformat()}Z\n\n"
        f"Sample Counts:\n"
        f"  • double_left_palm  : {counts.get('double_left_palm', 0)}\n"
        f"  • double_right_palm : {counts.get('double_right_palm', 0)}\n"
        f"  • noise_and_typing  : {counts.get('noise_and_typing', 0)}\n"
        f"  • TOTAL             : {counts.get('total', 0)}\n\n"
        f"Audit Results: {audit_passed}/{audit_total} passed ({audit_pct})\n"
        f"Format: 500ms @ 48kHz, 24000 samples/file, float32 .npy"
    )
    return msg


def pull_master_dataset(target_dir="dataset"):
    """Downloads the master dataset (HDF5 + raw .npy) from Hugging Face."""
    print(f"\n==========================================================")
    print(f" 📥 DOWNLOADING MASTER DATASET FROM HUGGING FACE          ")
    print(f"==========================================================")
    print(f" 🌐 Repository: https://huggingface.co/datasets/{HF_DATASET_REPO}")
    print(f" 📂 Target Directory: {os.path.abspath(target_dir)}")

    try:
        os.makedirs(target_dir, exist_ok=True)
        # Download entire repo (HDF5 + raw .npy folders)
        local_path = snapshot_download(
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            local_dir=target_dir
        )
        print(f" ✅ Downloaded full dataset (HDF5 + .npy) -> {local_path}")
        return local_path
    except Exception as e:
        print(f"❌ Error downloading dataset: {e}")
        return None


def push_contributions(local_folder="dataset_double_taps", contributor_name=None):
    """Pushes local dataset samples + manifest to Hugging Face LFS."""
    if not os.path.exists(local_folder):
        print(f"❌ Folder '{local_folder}' does not exist!")
        return False

    api = HfApi()
    laptop_model = detect_laptop_model()

    if not contributor_name:
        contributor_name = input(f"Enter your name or handle (e.g. manas, daksh): ").strip()
        if not contributor_name:
            contributor_name = "anonymous"

    # Auto-generate folder name from laptop model
    device_slug = laptop_model.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
    target_repo_path = f"contributions/{contributor_name}/{device_slug}"

    # Count samples
    counts = count_dataset_samples(local_folder)

    print(f"\n==========================================================")
    print(f" 📤 MORSE DATASET CONTRIBUTION                            ")
    print(f"==========================================================")
    print(f" 👤 Contributor  : {contributor_name}")
    print(f" 💻 Laptop Model : {laptop_model}")
    print(f" 🖥️ Platform     : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f" 📊 Samples      : Left={counts.get('double_left_palm',0)} | Right={counts.get('double_right_palm',0)} | Noise={counts.get('noise_and_typing',0)} | Total={counts['total']}")
    print(f" 🌐 HF Repo Path : {target_repo_path}")

    # Run audit
    print(f"\n⏳ Running dataset health audit before push...")
    audit_passed, audit_total = run_audit(local_folder)

    if audit_passed is not None:
        audit_pct = audit_passed / max(audit_total, 1) * 100
        print(f" 🔍 Audit Result : {audit_passed}/{audit_total} passed ({audit_pct:.1f}%)")

        if audit_pct < 70.0:
            print(f" ⚠️ WARNING: Audit pass rate is below 70%. Data quality may be low!")
            confirm = input(" Continue push anyway? (y/n): ").strip().lower()
            if confirm != "y":
                print(" ❌ Push cancelled.")
                return False
    else:
        audit_passed = counts["total"]
        audit_total = counts["total"]
        print(f" ⚠️ Audit module not available, skipping audit check.")

    # Build manifest
    manifest = build_contribution_manifest(
        local_folder, contributor_name, laptop_model, counts, audit_passed, audit_total
    )

    # Save manifest JSON alongside dataset
    manifest_path = os.path.join(local_folder, "contribution_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f" 📄 Saved contribution manifest -> {manifest_path}")

    # Build rich commit message
    commit_msg = build_commit_message(contributor_name, laptop_model, counts, audit_passed, audit_total)
    print(f"\n📝 Commit Message Preview:\n{'='*60}")
    print(commit_msg)
    print(f"{'='*60}\n")

    confirm = input("Push this contribution to Hugging Face? (y/n): ").strip().lower()
    if confirm != "y":
        print(" ❌ Push cancelled.")
        return False

    try:
        api.upload_folder(
            folder_path=local_folder,
            path_in_repo=target_repo_path,
            repo_id=HF_DATASET_REPO,
            repo_type="dataset",
            commit_message=commit_msg
        )
        print(f"\n ✅ Contribution pushed to Hugging Face!")
        print(f" 🌐 View at: https://huggingface.co/datasets/{HF_DATASET_REPO}/tree/main/{target_repo_path}")
        return True
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print("💡 Tip: Run 'huggingface-cli login' or set HF_TOKEN environment variable.")
        return False


def run_sync_menu():
    """CLI Menu for HF Dataset Pull & Push."""
    laptop_model = detect_laptop_model()
    while True:
        print("\n==========================================================")
        print("   MORSE TLM 1.5 — Hugging Face Dataset Sync Suite        ")
        print("==========================================================")
        print(f" 💻 Detected Laptop: {laptop_model}")
        print(f" 🖥️ Platform: {platform.system()} {platform.machine()}")
        print("----------------------------------------------------------")
        print(" 1. PULL Master Dataset (HDF5 + raw .npy files)")
        print(" 2. PUSH Local Dataset Contribution (with full audit)")
        print(" 3. Exit")
        print("----------------------------------------------------------")

        choice = input("Enter choice (1-3): ").strip()
        if choice == "1":
            pull_master_dataset()
        elif choice == "2":
            push_contributions()
        elif choice == "3":
            print("\n👋 Exiting Sync Suite.\n")
            break
        else:
            print("❌ Invalid selection.")


if __name__ == "__main__":
    run_sync_menu()
