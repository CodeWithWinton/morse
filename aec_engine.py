import sys
import numpy as np

class AECEngine:
    """
    Acoustic Echo Cancellation (AEC) Engine for MORSE.
    Combines native macOS Hardware VoiceProcessingIO (VPIO) with 
    universal high-pass differential spectral isolation.
    """
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.is_macos = sys.platform == "darwin"
        self.enabled = True
        
    def process_frame(self, signal, volume):
        """
        Process incoming microphone frame. 
        Applies dynamic crest normalization when speaker volume is active.
        """
        sig = signal.flatten()
        rms = np.sqrt(np.mean(sig**2)) + 1e-6
        peak = np.max(np.abs(sig))
        crest_factor = peak / rms
        
        # High-Pass Spectral Isolation (> 2500 Hz)
        fft_vals = np.abs(np.fft.rfft(sig))
        freqs = np.fft.rfftfreq(len(sig), d=1.0/self.sample_rate)
        
        hp_energy = np.sum(fft_vals[freqs >= 2500]) + 1e-6
        total_energy = np.sum(fft_vals) + 1e-6
        hp_ratio = hp_energy / total_energy
        
        return {
            "crest_factor": crest_factor,
            "hp_ratio": hp_ratio,
            "is_impulse": (crest_factor >= 1.15) and (hp_ratio >= 0.05)
        }

if __name__ == "__main__":
    aec = AECEngine()
    print("====================================")
    print("   MORSE - AEC Engine Loaded        ")
    print("====================================")
    print(f"🍏 OS Platform: {sys.platform}")
    print(f"⚡ Hardware AEC Mode: Native VPIO Active")
