import numpy as np
import sounddevice as sd

SAMPLE_RATE = 48000  # Native Apple Silicon Hardware Clock (0% OS Resampling)
WINDOW_SIZE = 2048   # 42.6ms window at 48.0kHz
DATASET_DIR = "dataset"

def extract_features(signal, original_rate=None):
    """Extract raw 1025-bin normalized FFT magnitude spectrum from audio buffer, with auto-resampling if needed."""
    sig = signal.flatten()
    
    # Auto-resample 44.1kHz dataset samples to 48.0kHz for 100% backward compatibility
    if original_rate and original_rate != SAMPLE_RATE:
        num_target_samples = int(len(sig) * SAMPLE_RATE / original_rate)
        sig = np.interp(
            np.linspace(0, len(sig), num_target_samples, endpoint=False),
            np.arange(len(sig)),
            sig
        )
        
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

def extract_2d_spectrogram(signal, original_rate=None, n_fft=256, hop_length=128):
    """Extract normalized 2D STFT Spectrogram matrix (Frequency vs Time) flattened to 1D feature array."""
    sig = signal.flatten()
    if original_rate and original_rate != SAMPLE_RATE:
        num_target_samples = int(len(sig) * SAMPLE_RATE / original_rate)
        sig = np.interp(
            np.linspace(0, len(sig), num_target_samples, endpoint=False),
            np.arange(len(sig)),
            sig
        )
        
    if len(sig) < WINDOW_SIZE:
        sig = np.pad(sig, (0, WINDOW_SIZE - len(sig)))
    elif len(sig) > WINDOW_SIZE:
        sig = sig[-WINDOW_SIZE:]
        
    num_frames = (len(sig) - n_fft) // hop_length + 1
    spectrogram = []
    window = np.hanning(n_fft)
    
    for i in range(num_frames):
        start = i * hop_length
        frame = sig[start:start + n_fft] * window
        fft_frame = np.abs(np.fft.rfft(frame))
        spectrogram.append(fft_frame)
        
    spec_matrix = np.array(spectrogram).T # 129 bins x 15 time frames = 1935 pixels
    max_val = np.max(spec_matrix)
    if max_val > 0:
        spec_matrix = spec_matrix / max_val
    return spec_matrix.flatten()

def load_dataset(categories):
    """Load and extract 1D features for all specified dataset categories (.npy and .wav supported)."""
    import os
    from scipy.io import wavfile
    X, y = [], []
    for label_idx, cat in enumerate(categories):
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy") or f.endswith(".wav")]
        for f in files:
            filepath = os.path.join(cat_dir, f)
            if f.endswith(".wav"):
                sr, signal = wavfile.read(filepath)
                signal = signal.astype(np.float32) / 32767.0
            else:
                signal = np.load(filepath)
                sr = SAMPLE_RATE
            X.append(extract_features(signal, original_rate=sr))
            y.append(label_idx)
    return np.array(X), np.array(y)

def load_dataset_2d(categories):
    """Load and extract 2D Spectrogram features for all specified dataset categories (.npy and .wav supported)."""
    import os
    from scipy.io import wavfile
    X, y = [], []
    for label_idx, cat in enumerate(categories):
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy") or f.endswith(".wav")]
        for f in files:
            filepath = os.path.join(cat_dir, f)
            if f.endswith(".wav"):
                sr, signal = wavfile.read(filepath)
                signal = signal.astype(np.float32) / 32767.0
            else:
                signal = np.load(filepath)
                sr = SAMPLE_RATE
            X.append(extract_2d_spectrogram(signal, original_rate=sr))
            y.append(label_idx)
            
            # Data Augmentation: For right_palm_rest, generate 1.25x and 0.80x scale copies for volume invariance
            if cat == "right_palm_rest":
                X.append(extract_2d_spectrogram(signal * 1.25, original_rate=sr))
                y.append(label_idx)
                X.append(extract_2d_spectrogram(signal * 0.80, original_rate=sr))
                y.append(label_idx)
    return np.array(X), np.array(y)
