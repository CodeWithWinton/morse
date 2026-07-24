import numpy as np

SAMPLE_RATE = 44100

def classify_audio_frame(sig, sample_rate=SAMPLE_RATE):
    """
    DSP Filter evaluating Low-to-High Frequency Energy Ratio and Crest Factor (Impulsiveness).
    Returns (is_tap, ratio, crest_factor, volume)
    """
    sig = sig.flatten()
    volume = np.linalg.norm(sig) * 10
    
    if volume < 3.5:
        return False, 0.0, 0.0, volume
        
    # 1. Isolate Peak Transient Window (around max amplitude)
    peak_idx = np.argmax(np.abs(sig))
    start_idx = max(0, peak_idx - 50)
    end_idx = min(len(sig), peak_idx + 800)
    transient = sig[start_idx:end_idx]
    
    if len(transient) < 100:
        return False, 0.0, 0.0, volume
        
    # 2. Frequency Energies on Transient
    fft_vals = np.abs(np.fft.rfft(transient))
    freqs = np.fft.rfftfreq(len(transient), d=1.0/sample_rate)
    
    low_energy = np.sum(fft_vals[(freqs >= 50) & (freqs <= 600)])
    high_energy = np.sum(fft_vals[freqs > 1500]) + 1e-6
    ratio = low_energy / high_energy
    
    # 3. Crest Factor (Impulsiveness = Peak / RMS on Transient)
    rms = np.sqrt(np.mean(transient**2)) + 1e-6
    peak = np.max(np.abs(transient))
    crest_factor = peak / rms
    
    # Optimized Physical Aluminum Resonance Rule:
    # 284 Tap Avg Ratio: 2.33
    # Typing Avg Ratio: 0.72 | Noise Avg Ratio: 1.11
    is_tap = (ratio > 1.25)
    
    return is_tap, ratio, crest_factor, volume
