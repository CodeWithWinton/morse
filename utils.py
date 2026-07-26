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
    flattened_spec = spec_matrix.flatten()

    # --- Rich Physical Acoustic Feature Extraction ---
    fft_full = np.abs(np.fft.rfft(sig))
    total_energy = np.sum(fft_full) + 1e-6
    freqs = np.fft.rfftfreq(len(sig), d=1.0/SAMPLE_RATE)
    
    # 1. Bass Energy Ratio (120 - 600 Hz aluminum structural resonance)
    bass_ratio = np.sum(fft_full[(freqs >= 120) & (freqs <= 600)]) / total_energy
    
    # 2. High-Pass Energy Ratio (> 2500 Hz metal ping)
    hp_ratio = np.sum(fft_full[freqs >= 2500]) / total_energy
    
    # 3. Spectral Centroid (Hz)
    centroid = np.sum(freqs * fft_full) / total_energy
    
    # 4. Spectral Rolloff (Frequency below which 85% energy lies)
    cum_energy = np.cumsum(fft_full)
    rolloff_idx = np.where(cum_energy >= 0.85 * total_energy)[0]
    rolloff = freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else 0.0
    
    # 5. Zero Crossing Rate (ZCR)
    zcr = np.mean(np.abs(np.diff(np.signbit(sig))))
    
    # 6. Spectral Flatness (Geometric Mean / Arithmetic Mean)
    gmean = np.exp(np.mean(np.log(fft_full + 1e-6)))
    amean = np.mean(fft_full) + 1e-6
    flatness = gmean / amean
    
    # 7. Fundamental Pitch Mode (Hz via Autocorrelation)
    autocorr = np.correlate(sig, sig, mode='full')
    autocorr = autocorr[len(autocorr)//2:]
    d_autocorr = np.diff(autocorr)
    start_search = int(SAMPLE_RATE / 1000) # Min 1000 Hz search range
    if len(d_autocorr) > start_search:
        peak_idx = np.argmax(autocorr[start_search:]) + start_search
        pitch = SAMPLE_RATE / peak_idx if peak_idx > 0 else 0.0
    else:
        pitch = 0.0

    # Append 7 Physical Features to 2D Spectrogram Array
    phys_features = np.array([bass_ratio, hp_ratio, centroid / 10000.0, rolloff / 10000.0, zcr, flatness, pitch / 10000.0])
    return np.concatenate([flattened_spec, phys_features])

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
            
            # Data Augmentation for 1:1 Dataset Equilibrium & Volume Invariance
            if cat == "right_palm_rest":
                X.append(extract_2d_spectrogram(signal * 1.25, original_rate=sr))
                y.append(label_idx)
                X.append(extract_2d_spectrogram(signal * 0.80, original_rate=sr))
                y.append(label_idx)
            elif cat == "left_palm_rest":
                X.append(extract_2d_spectrogram(signal * 1.15, original_rate=sr))
                y.append(label_idx)
    return np.array(X), np.array(y)
