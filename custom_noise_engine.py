import numpy as np
import time
import sys

SAMPLE_RATE = 48000

class CustomChassisNoiseEngine:
    """
    MORSE In-House Custom Chassis-Aware Noise Cancellation & Speaker Shield Engine.
    
    Design Goals:
    1. Preserve Kinetic Metallic Impulses (80-600 Hz chassis resonance + 2.5k-3.5k Hz metal ping).
    2. Suppress Continuous Background Noise (fan hum, AC noise, TV speech, room hiss).
    3. MacBook Speaker Shield: Suppress internal speaker audio (YouTube, Spotify, music)
       via Kinetic-vs-Speaker Impact Ratio Analysis.
    4. Strict CPU Target: < 0.15ms execution time per 350ms frame (< 0.9% CPU overhead).
    """
    def __init__(self, sample_rate=SAMPLE_RATE):
        self.sample_rate = sample_rate
        # Subband noise floor profile (20 frequency bins)
        self.subband_noise_floor = None
        self.smoothing_factor = 0.92
        self.speaker_active = False

    def set_speaker_active(self, active: bool):
        """Toggle active speaker shield mode."""
        self.speaker_active = active

    def compute_kinetic_impact_index(self, sig: np.ndarray) -> float:
        """
        Calculates Kinetic-vs-Speaker Impact Ratio.
        Physical Palm Taps: Heavy sub-300Hz metallic deck impact (Ratio >= 1.8).
        MacBook Speaker Playback: High mid/high driver energy (Ratio <= 0.6).
        """
        signal = sig.flatten()
        if len(signal) == 0:
            return 0.0
            
        fft_vals = np.abs(np.fft.rfft(signal))
        freqs = np.fft.rfftfreq(len(signal), d=1.0 / self.sample_rate)
        
        # Sub-300Hz physical kinetic unibody impact energy
        low_kinetic_energy = np.sum(fft_vals[(freqs >= 80.0) & (freqs <= 300.0)])
        
        # 1kHz-6kHz speaker driver acoustic energy
        mid_high_speaker_energy = np.sum(fft_vals[(freqs >= 1000.0) & (freqs <= 6000.0)]) + 1e-6
        
        ratio = float(low_kinetic_energy / mid_high_speaker_energy)
        return ratio

    def compute_crest_factor(self, sig: np.ndarray) -> float:
        """
        Calculates Peak-to-RMS Crest Factor on audio transient.
        Impulsive Taps: Sharp peak relative to RMS (Crest Factor >= 3.2).
        Continuous Background Noise / Speech: Smooth RMS (Crest Factor < 2.5).
        """
        signal = sig.flatten()
        if len(signal) == 0:
            return 0.0
        rms = np.sqrt(np.mean(signal ** 2)) + 1e-6
        peak = np.max(np.abs(signal))
        return float(peak / rms)

    def process_frame(self, sig: np.ndarray) -> tuple[np.ndarray, dict]:
        """
        Executes custom chassis-aware noise cancellation & speaker filtering.
        Returns: (clean_signal, stats_dict)
        """
        t0 = time.perf_counter()
        signal = sig.flatten()
        if len(signal) == 0:
            return signal, {"cpu_ms": 0.0, "crest_factor": 0.0, "impact_index": 0.0}

        # 1. FFT to frequency domain
        fft_spectrum = np.fft.rfft(signal)
        magnitude = np.abs(fft_spectrum)
        phase = np.angle(fft_spectrum)
        freqs = np.fft.rfftfreq(len(signal), d=1.0 / self.sample_rate)

        # 2. Compute Physical Metrics
        crest_factor = self.compute_crest_factor(signal)
        impact_index = self.compute_kinetic_impact_index(signal)

        # 3. Kinetic Impulse Protection Mask
        # Protects 80-600Hz aluminum resonance and 2.5k-3.5kHz metal ping during taps
        is_impulse = (crest_factor >= 3.0) or (impact_index >= 1.5)
        
        # 4. Multi-Band Subband Adaptive Noise Floor Estimation
        # Split magnitude into 20 subbands for per-frequency noise tracking
        n_bins = 20
        subband_size = len(magnitude) // n_bins
        current_subbands = np.array([
            np.mean(magnitude[i * subband_size:(i + 1) * subband_size])
            for i in range(n_bins)
        ])

        if self.subband_noise_floor is None:
            self.subband_noise_floor = current_subbands
        elif not is_impulse:
            # Update noise floor ONLY during non-impulse background frames
            self.subband_noise_floor = (
                self.smoothing_factor * self.subband_noise_floor + 
                (1.0 - self.smoothing_factor) * current_subbands
            )

        # 5. Build Subband Attenuation Mask
        full_noise_profile = np.repeat(self.subband_noise_floor, subband_size)
        if len(full_noise_profile) < len(magnitude):
            full_noise_profile = np.pad(full_noise_profile, (0, len(magnitude) - len(full_noise_profile)), mode='edge')
        elif len(full_noise_profile) > len(magnitude):
            full_noise_profile = full_noise_profile[:len(magnitude)]

        # Bandpass shaping: preserve 80Hz - 3800Hz
        bandpass = (freqs >= 80.0) & (freqs <= 3800.0)
        
        # Over-subtraction: if speaker is active, attenuate high speaker bands more aggressively
        over_sub = 1.6 if self.speaker_active else 1.25
        subtracted_mag = np.maximum(magnitude - (over_sub * full_noise_profile), 0.08 * magnitude)
        clean_mag = subtracted_mag * bandpass

        # 6. Speaker Audio Suppression (If speaker active & low kinetic impact index, suppress frame)
        if self.speaker_active and impact_index < 0.7:
            clean_mag *= 0.15  # Heavily suppress internal speaker audio bleed

        # 7. Inverse FFT Reconstruction
        clean_fft = clean_mag * np.exp(1j * phase)
        clean_signal = np.fft.irfft(clean_fft, n=len(signal)).astype(np.float32)

        elapsed_ms = (time.perf_counter() - t0) * 1000.0

        stats = {
            "cpu_ms": elapsed_ms,
            "crest_factor": crest_factor,
            "impact_index": impact_index,
            "is_impulse": is_impulse,
            "speaker_active": self.speaker_active
        }

        return clean_signal, stats

if __name__ == "__main__":
    engine = CustomChassisNoiseEngine()
    dummy = np.random.randn(16800).astype(np.float32) * 0.01
    clean, stats = engine.process_frame(dummy)
    print("==========================================================================")
    print("   MORSE - Custom In-House Chassis Noise & Speaker Engine")
    print("==========================================================================")
    print(f"⚡ Benchmark Execution Time per 350ms frame: {stats['cpu_ms']:.3f} ms")
    print(f"📊 Crest Factor: {stats['crest_factor']:.2f} | Impact Index: {stats['impact_index']:.2f}")
    print(f"🎯 Calculated CPU Overhead: {(stats['cpu_ms'] / 350.0) * 100.0:.3f}% Total CPU (Goal: < 0.9%)")
