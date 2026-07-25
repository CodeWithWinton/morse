import numpy as np
import sounddevice as sd

SAMPLE_RATE = 44100
WINDOW_SIZE = 2048  # 46.4ms window at 44.1kHz
DATASET_DIR = "dataset"

def extract_features(signal):
    """Extract raw 1025-bin normalized FFT magnitude spectrum from audio buffer."""
    sig = signal.flatten()
    if len(sig) < WINDOW_SIZE:
        sig = np.pad(sig, (0, WINDOW_SIZE - len(sig)))
    elif len(sig) > WINDOW_SIZE:
        sig = sig[-WINDOW_SIZE:]
        
    fft_vals = np.abs(np.fft.rfft(sig))
    max_val = np.max(fft_vals)
    if max_val > 0:
        fft_vals = fft_vals / max_val
    return fft_vals

def find_builtin_mic():
    """Find and return the hardware device ID for built-in microphone."""
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0 and ("built-in" in dev['name'].lower() or "macbook" in dev['name'].lower()):
            return i, dev['name']
    return None, "Default Microphone"

def load_dataset(categories):
    """Load and extract features for all specified dataset categories."""
    import os
    X, y = [], []
    for label_idx, cat in enumerate(categories):
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy")]
        for f in files:
            signal = np.load(os.path.join(cat_dir, f))
            X.append(extract_features(signal))
            y.append(label_idx)
    return np.array(X), np.array(y)
