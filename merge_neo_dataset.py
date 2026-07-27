import h5py
import os
import glob
import numpy as np

MAIN_H5 = "morse_dataset.h5"
NEO_H5  = "neo_dataset.h5"
DATASET_DIR = "dataset_double_taps"
CATEGORIES = ["double_left_palm", "double_right_palm", "noise_and_typing"]

def merge_hdf5():
    """Merge neo_dataset.h5 directly into morse_dataset.h5."""
    if not os.path.exists(NEO_H5):
        print(f"❌ '{NEO_H5}' not found in current directory!")
        print("   Please AirDrop 'morse_dataset.h5' from MacBook Neo, rename it to 'neo_dataset.h5', and place it here.")
        return False
        
    print(f"📦 Merging '{NEO_H5}' into '{MAIN_H5}'...")
    
    with h5py.File(MAIN_H5, "a") as main_f, h5py.File(NEO_H5, "r") as neo_f:
        for cat in CATEGORIES:
            if cat in neo_f:
                neo_data = neo_f[cat][:]
                if cat not in main_f:
                    main_f.create_dataset(cat, data=neo_data, maxshape=(None, 24000), chunks=True, dtype="float32")
                else:
                    curr_len = main_f[cat].shape[0]
                    new_len = curr_len + neo_data.shape[0]
                    main_f[cat].resize((new_len, 24000))
                    main_f[cat][curr_len:new_len] = neo_data
                print(f"  ✅ Merged {len(neo_data)} samples for '{cat}'!")
                
    print("\n🎉 HDF5 Merge Completed Successfully!")
    return True

def sync_npy_to_h5():
    """Re-pack all .npy files from dataset_double_taps into morse_dataset.h5."""
    print(f"📄 Packing all .npy files from '{DATASET_DIR}' into '{MAIN_H5}'...")
    with h5py.File(MAIN_H5, "w") as h5f:
        for cat in CATEGORIES:
            folder = os.path.join(DATASET_DIR, cat)
            if not os.path.exists(folder):
                continue
            files = sorted(glob.glob(os.path.join(folder, "*.npy")))
            if not files:
                continue
            samples = []
            for f in files:
                arr = np.load(f).astype(np.float32)
                if len(arr) == 24000:
                    samples.append(arr)
            if samples:
                mat = np.array(samples, dtype=np.float32)
                h5f.create_dataset(cat, data=mat, maxshape=(None, 24000), chunks=True, dtype="float32")
                print(f"  ⚡ Packed {len(mat)} samples for '{cat}'")
    print("\n🎉 Master HDF5 Container Repacked Successfully!")

if __name__ == "__main__":
    if os.path.exists(NEO_H5):
        merge_hdf5()
    else:
        sync_npy_to_h5()
