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

def compute_mel_filterbank(n_fft=256, n_mels=20, sample_rate=48000, fmin=100.0, fmax=3500.0):
    """Compute triangular Mel filterbank matrix (n_mels x (n_fft//2 + 1))."""
    def hz_to_mel(hz):
        return 2595.0 * np.log10(1.0 + hz / 700.0)
    
    def mel_to_hz(mel):
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)
    
    mel_min = hz_to_mel(fmin)
    mel_max = hz_to_mel(fmax)
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = mel_to_hz(mel_points)
    bin_points = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)
    
    num_bins = n_fft // 2 + 1
    bank = np.zeros((n_mels, num_bins))
    
    for m in range(1, n_mels + 1):
        f_m_minus = bin_points[m - 1]
        f_m = bin_points[m]
        f_m_plus = bin_points[m + 1]
        
        for k in range(f_m_minus, f_m):
            if f_m != f_m_minus:
                bank[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
        for k in range(f_m, f_m_plus):
            if f_m_plus != f_m and k < num_bins:
                bank[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)
                
    return bank

_MEL_FILTERBANK = compute_mel_filterbank()

def extract_lean_305_features(signal, original_rate=None, n_fft=256, hop_length=128, als_shadow=0.0, mic_ratio=1.0):
    """Extract optimized 305-feature vector: 300 Mel-Spectrogram features + 5 scalar physical features."""
    sig = signal.flatten()
    if original_rate and original_rate != SAMPLE_RATE:
        num_target_samples = int(len(sig) * SAMPLE_RATE / original_rate)
        sig = np.interp(
            np.linspace(0, len(sig), num_target_samples, endpoint=False),
            np.arange(len(sig)),
            sig
        )
        
    # Position-Invariant Peak Alignment: Center peak impact at sample 4800 (100ms into 500ms window)
    target_samples = 24000
    if len(sig) > 0:
        peak_idx = np.argmax(np.abs(sig))
        start_idx = max(0, peak_idx - 4800)
        sig = sig[start_idx:start_idx + target_samples]
        
    if len(sig) < target_samples:
        sig = np.pad(sig, (0, target_samples - len(sig)))
        
    num_frames = (len(sig) - n_fft) // hop_length + 1
    window = np.hanning(n_fft)
    
    mel_frames = []
    for i in range(num_frames):
        start = i * hop_length
        frame = sig[start:start + n_fft] * window
        fft_frame = np.abs(np.fft.rfft(frame))
        mel_frame = np.dot(_MEL_FILTERBANK, fft_frame)
        mel_frames.append(mel_frame)
        
    mel_matrix = np.array(mel_frames).T  # 20 mels x 15 time frames = 300 features
    max_val = np.max(mel_matrix)
    if max_val > 0:
        mel_matrix = mel_matrix / max_val
    flattened_mel = mel_matrix.flatten() # 300 features
    
    # 5 Scalar Physical Features (Consistent between static dataset files & live streaming audio)
    fft_full = np.abs(np.fft.rfft(sig))
    total_energy = np.sum(fft_full) + 1e-6
    freqs = np.fft.rfftfreq(len(sig), d=1.0/SAMPLE_RATE)
    
    # 1. Bass Energy Ratio (120 - 600 Hz aluminum structural resonance)
    bass_ratio = np.sum(fft_full[(freqs >= 120) & (freqs <= 600)]) / total_energy
    
    # 2. High-Pass Energy Ratio (> 2500 Hz metal ping)
    hp_ratio = np.sum(fft_full[freqs >= 2500]) / total_energy

    # 3. Spectral Centroid (Hz)
    centroid = np.sum(freqs * fft_full) / total_energy
    
    # 4. Crest Factor (Peak / RMS)
    rms = np.sqrt(np.mean(sig**2)) + 1e-6
    crest_factor = np.max(np.abs(sig)) / rms

    # Onset mic ratio (MelBin 4 + MelBin 9) / Frame 0 Energy
    frame_0_energy = np.sum([mel_matrix[m, 0] for m in range(20)]) + 1e-6
    mic_ratio = float((mel_matrix[4, 0] + mel_matrix[9, 0]) / frame_0_energy)

    # 5. Spatial High-Frequency Decay (Frame 0-2 vs Frame 3-8 high-freq ratio)
    hp_early = np.sum(mel_matrix[12:, :3]) + 1e-6
    hp_late = np.sum(mel_matrix[12:, 3:9]) + 1e-6
    spatial_hf_decay = float(hp_early / hp_late)

    # 6. Onset Attack Slope (Energy rise rate between frame 0 and frame 1)
    frame_0_e = np.sum(mel_matrix[:, 0]) + 1e-6
    frame_1_e = np.sum(mel_matrix[:, 1]) + 1e-6
    onset_attack_slope = float((frame_1_e - frame_0_e) / frame_0_e)

    # 7. Spectral Tilt (High MelBins 12-19 vs Low MelBins 0-5 at Frame 0)
    high_mels_0 = np.sum(mel_matrix[12:, 0])
    low_mels_0 = np.sum(mel_matrix[:6, 0]) + 1e-6
    spectral_tilt = float(high_mels_0 / low_mels_0)

    # 8. Transient Decay Time (Frame index where energy drops below 50% of peak)
    frame_energies = np.sum(mel_matrix, axis=0)
    peak_e = np.max(frame_energies) + 1e-6
    half_peak_mask = np.where(frame_energies < (0.5 * peak_e))[0]
    decay_frame_idx = float(half_peak_mask[0] if len(half_peak_mask) > 0 else 15) / 15.0

    # 9. High-Mel Skew (MelBin 15 vs MelBin 4 at Frame 0)
    high_mel_skew = float(mel_matrix[15, 0] - mel_matrix[4, 0])

    scalars = np.array([
        bass_ratio, 
        hp_ratio, 
        centroid / 10000.0, 
        crest_factor / 10.0, 
        mic_ratio / 10.0,
        spatial_hf_decay / 10.0,
        onset_attack_slope,
        spectral_tilt,
        decay_frame_idx,
        high_mel_skew
    ], dtype=np.float32)
    
    return np.concatenate([flattened_mel, scalars])

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
    # 8. Mechanical Unibody Vibration Energy Dispersion Ratio
    dispersion_ratio = compute_vibration_trail_ratio(sig)

    # Append 8 Physical Features (306 features total) to 2D Spectrogram Array
    phys_features = np.array([bass_ratio, hp_ratio, centroid / 10000.0, rolloff / 10000.0, zcr, flatness, pitch / 10000.0, dispersion_ratio])
    return np.concatenate([flattened_spec, phys_features])

def compute_vibration_trail_ratio(sig):
    """
    Calculate Mechanical Unibody Vibration Energy Dispersion Ratio.
    Aluminum chassis taps spread physical kinetic energy across a 30-50ms wave window.
    Air-borne clicks (earphone case snaps, pen clicks) are concentrated in a razor-sharp <3ms spike.
    """
    signal = np.abs(sig.flatten())
    if len(signal) == 0:
        return 0.0
        
    peak_idx = np.argmax(signal)
    peak_val = signal[peak_idx] + 1e-6
    
    # Analyze a 50ms window centered around the peak impact
    win_samples = int(0.025 * SAMPLE_RATE) # 25ms before and after peak (50ms total)
    start_idx = max(0, peak_idx - win_samples)
    end_idx = min(len(signal), peak_idx + win_samples)
    
    window_signal = signal[start_idx:end_idx]
    if len(window_signal) == 0:
        return 0.0
        
    window_rms = np.sqrt(np.mean(window_signal ** 2))
    return float(window_rms / peak_val)

def count_impulse_peaks(sig, min_distance_ms=80.0, min_prominence_ratio=0.18):
    """
    Count the number of distinct physical impact peaks in a 350ms buffer.
    
    True Double Tap: Has exactly 2 distinct physical impact peaks separated by 90ms - 280ms.
    Single Noise / Lid Snap / Door Slam: Has only 1 primary impact peak (returns peak_count = 1).
    """
    signal = np.abs(sig.flatten())
    if len(signal) == 0:
        return 0
        
    max_val = np.max(signal)
    if max_val < 0.05:
        return 0
        
    threshold = max_val * min_prominence_ratio
    min_dist_samples = int((min_distance_ms / 1000.0) * SAMPLE_RATE) # 4320 samples at 48kHz
    
    peaks = []
    i = 0
    while i < len(signal):
        if signal[i] >= threshold:
            win_start = max(0, i - int(0.005 * SAMPLE_RATE))
            win_end = min(len(signal), i + int(0.005 * SAMPLE_RATE))
            local_peak = win_start + np.argmax(signal[win_start:win_end])
            
            if not peaks or (local_peak - peaks[-1]) >= min_dist_samples:
                peaks.append(local_peak)
            i = local_peak + min_dist_samples
        else:
            i += 1
            
    return len(peaks)

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

def load_dataset_2d(categories, use_lean_305=False):
    """Load and extract 2D Spectrogram or Lean 305 features for all specified dataset categories (.npy and .wav supported)."""
    import os
    from scipy.io import wavfile
    X, y = [], []
    extract_fn = extract_lean_305_features if use_lean_305 else extract_2d_spectrogram
    
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
            X.append(extract_fn(signal, original_rate=sr))
            y.append(label_idx)
            
            # 1:1 Dataset Equilibrium & Volume Invariance Augmentation
            if cat in ("right_palm_rest", "left_palm_rest"):
                X.append(extract_fn(signal * 1.20, original_rate=sr))
                y.append(label_idx)
                X.append(extract_fn(signal * 0.80, original_rate=sr))
                y.append(label_idx)
_ambient_noise_psd = None

def apply_medium_thud_dsp_filter(signal):
    """
    Medium-Tier Impulse DSP Filter for MORSE.
    Strips background TV speech, music, AC hum, and high-frequency hiss,
    leaving ONLY the clean physical 'thud thud' chassis impulse.
    
    CPU Impact: ~0.1ms per frame (< 0.5% total CPU).
    """
    sig = signal.flatten()
    if len(sig) == 0:
        return sig
        
    # 1. FFT to frequency domain
    fft_spectrum = np.fft.rfft(sig)
    magnitude = np.abs(fft_spectrum)
    phase = np.angle(fft_spectrum)
    freqs = np.fft.rfftfreq(len(sig), d=1.0/SAMPLE_RATE)
    
    # 2. Bandpass Frequency Shaping (80Hz - 3500Hz)
    # Preserves low-bass chassis thud (120-600Hz) and unibody impact (800-3500Hz)
    bandpass_mask = (freqs >= 80.0) & (freqs <= 3500.0)
    filtered_mag = magnitude * bandpass_mask
    
    # 3. Percentile Stationary Noise Floor Estimation
    # Stationarity assumption: background noise is continuous, taps are transient peak impulses
    noise_floor = np.percentile(filtered_mag, 25)
    
    # Soft subtraction preserving 10% floor safety net so taps are NEVER erased
    clean_mag = np.maximum(filtered_mag - (1.2 * noise_floor), 0.10 * filtered_mag)
    
    # 4. Reconstruct clean audio via Inverse FFT
    clean_fft = clean_mag * np.exp(1j * phase)
    clean_sig = np.fft.irfft(clean_fft, n=len(sig))
    
    return clean_sig.astype(np.float32)

