import sys
import ctypes
import os
import numpy as np

class AECEngine:
    """
    Acoustic Echo Cancellation (AEC) Engine for MORSE.
    Loads Apple Silicon Hardware VoiceProcessingIO (VPIO) via vpio_bridge.dylib.
    """
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.is_macos = sys.platform == "darwin"
        self.vpio_lib = None
        self.hardware_aec_active = False
        
        if self.is_macos:
            dylib_path = os.path.join(os.path.dirname(__file__), "vpio_bridge.dylib")
            if os.path.exists(dylib_path):
                try:
                    self.vpio_lib = ctypes.CDLL(dylib_path)
                    res = self.vpio_lib.enable_vpio(self.sample_rate)
                    if res == 0:
                        self.hardware_aec_active = True
                except Exception as e:
                    self.hardware_aec_active = False

    def process_frame(self, signal, volume):
        sig = signal.flatten()
        rms = np.sqrt(np.mean(sig**2)) + 1e-6
        peak = np.max(np.abs(sig))
        crest_factor = peak / rms
        
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

    def close(self):
        if self.vpio_lib and self.hardware_aec_active:
            try:
                self.vpio_lib.disable_vpio()
            except Exception:
                pass
            self.hardware_aec_active = False

if __name__ == "__main__":
    aec = AECEngine()
    print("====================================")
    print("   MORSE - Hardware AEC Engine      ")
    print("====================================")
    print(f"🍏 OS Platform: {sys.platform}")
    print(f"⚡ Native VPIO Hardware AEC: {'ACTIVE (0% CPU)' if aec.hardware_aec_active else 'FALLBACK'}")
    aec.close()
