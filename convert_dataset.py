import os
import glob
import time
import h5py
import numpy as np

SOURCE_DIR = "dataset_double_taps"
CATEGORIES = ["double_left_palm", "double_right_palm", "noise_and_typing"]
H5_FILEPATH = "morse_dataset.h5"

def convert_npy_to_h5():
    print("==========================================================================")
    print("   MORSE - HDF5 Dataset Compiler (float32 Dual-Engine Format)            ")
    print("==========================================================================")
    
    if not os.path.exists(SOURCE_DIR):
        print(f"❌ Source dataset directory '{SOURCE_DIR}' not found!")
        return

    t0 = time.time()
    total_converted = 0

    with h5py.File(H5_FILEPATH, "w") as h5f:
        # Save dataset root metadata attributes
        h5f.attrs["model_target"] = "TLM 1.0 Double-Tap"
        h5f.attrs["dtype"] = "float32"
        h5f.attrs["sample_rate"] = 48000
        h5f.attrs["created_timestamp"] = time.ctime()

        for cat in CATEGORIES:
            cat_dir = os.path.join(SOURCE_DIR, cat)
            if not os.path.exists(cat_dir):
                continue

            npy_files = sorted(glob.glob(os.path.join(cat_dir, "*.npy")))
            print(f"  • Packing {len(npy_files):4d} samples for '{cat.upper()}'...")

            samples = []
            target_len = 24000  # 500ms window at 48kHz (Full double-tap impact 1 + gap + impact 2 + decay)
            for f in npy_files:
                arr = np.load(f).flatten().astype(np.float32)
                if len(arr) < target_len:
                    arr = np.pad(arr, (0, target_len - len(arr)))
                elif len(arr) > target_len:
                    arr = arr[:target_len]
                samples.append(arr)

            if len(samples) > 0:
                data_matrix = np.array(samples, dtype=np.float32)
                sample_shape = data_matrix.shape[1:]

                # Create resizable chunked HDF5 dataset for fast live appending
                dset = h5f.create_dataset(
                    cat,
                    data=data_matrix,
                    maxshape=(None,) + sample_shape,
                    chunks=True,
                    compression="gzip",
                    compression_opts=4
                )
                dset.attrs["count"] = len(samples)
                total_converted += len(samples)

    elapsed = time.time() - t0
    h5_size_mb = os.path.getsize(H5_FILEPATH) / (1024 * 1024)

    print("\n==========================================================================")
    print(" 📊 CONVERSION SUMMARY & BENCHMARK")
    print("==========================================================================")
    print(f"  ✅ Total Samples Packed : {total_converted:,} samples")
    print(f"  📄 Saved HDF5 File      : file://{os.path.abspath(H5_FILEPATH)}")
    print(f"  💾 HDF5 File Size       : {h5_size_mb:.2f} MB")
    print(f"  ⚡ Total Time Elapsed   : {elapsed:.2f} seconds")
    print("\n🎉 `morse_dataset.h5` is ready for ultra-fast training and live appends!\n")

def append_sample_to_h5(category: str, signal: np.ndarray, h5_path: str = H5_FILEPATH):
    """
    Utility function to append a single raw float32 signal vector live into morse_dataset.h5.
    Used by auto_stream_collector.py and daily_data_collector.py during live tap collection.
    """
    sig = signal.flatten().astype(np.float32)
    with h5py.File(h5_path, "a") as h5f:
        if category in h5f:
            dset = h5f[category]
            old_len = dset.shape[0]
            dset.resize((old_len + 1, sig.shape[0]))
            dset[old_len] = sig
            dset.attrs["count"] = old_len + 1
        else:
            dset = h5f.create_dataset(
                category,
                data=np.array([sig], dtype=np.float32),
                maxshape=(None, sig.shape[0]),
                chunks=True,
                compression="gzip",
                compression_opts=4
            )
            dset.attrs["count"] = 1

if __name__ == "__main__":
    convert_npy_to_h5()
