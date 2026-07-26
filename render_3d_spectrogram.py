import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.io import wavfile
import os
import sys

from utils import SAMPLE_RATE, WINDOW_SIZE

def render_3d_spectrogram(audio_signal, sample_rate=48000, title="3D STFT Spectrogram Surface Mesh"):
    """
    Renders a 3D Topographical STFT Spectrogram Surface Mesh (Time x Frequency x Energy).
    Highlights physical double-tap 'Dual Volcano Spikes' in 3D space.
    """
    # 2D Short-Time Fourier Transform (STFT)
    n_fft = 256
    hop_length = 64
    
    stft = np.abs(np.lib.stride_tricks.sliding_window_view(audio_signal, n_fft)[::hop_length])
    fft_window = np.hanning(n_fft)
    stft_matrix = np.abs(np.fft.rfft(stft * fft_window, axis=1)).T  # (129 freqs x N time frames)
    
    # Energy in dB
    stft_db = 20 * np.log10(stft_matrix + 1e-5)
    
    time_frames = np.linspace(0, len(audio_signal) / sample_rate * 1000, stft_matrix.shape[1])
    freq_bins = np.linspace(0, sample_rate / 2 / 1000, stft_matrix.shape[0])  # kHz
    
    T, F = np.meshgrid(time_frames, freq_bins)
    
    # 3D Plotting
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    surf = ax.plot_surface(T, F, stft_db, cmap='magma', edgecolor='none', alpha=0.9)
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel('Time (ms)', fontsize=11, labelpad=10)
    ax.set_ylabel('Frequency (kHz)', fontsize=11, labelpad=10)
    ax.set_zlabel('Energy Magnitude (dB)', fontsize=11, labelpad=10)
    
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10, label='Spectral Power Density (dB)')
    
    # Set optimal 3D viewing angle
    ax.view_init(elev=35, azim=-55)
    
    plt.tight_layout()
    output_png = "3d_spectrogram_surface.png"
    plt.savefig(output_png, dpi=200)
    print(f"✅ Saved 3D Spectrogram Surface Render to '{output_png}'!")
    plt.show()

if __name__ == "__main__":
    wav_file = "filtered_tap.wav" if os.path.exists("filtered_tap.wav") else ("raw_tap.wav" if os.path.exists("raw_tap.wav") else None)
    if wav_file:
        sr, sig = wavfile.read(wav_file)
        sig = sig.astype(np.float32) / 32767.0
        render_3d_spectrogram(sig, sample_rate=sr, title=f"3D Double-Tap Spectrogram Surface ({wav_file})")
    else:
        # Generate synthetic 3D Double-Tap Dual Volcano Surface for demo
        t = np.linspace(0, 0.4, 19200)
        tap1 = np.sin(2 * np.pi * 350 * t) * np.exp(-(t - 0.1)**2 / 0.001)
        tap2 = np.sin(2 * np.pi * 350 * t) * np.exp(-(t - 0.28)**2 / 0.001)
        synthetic_signal = (tap1 + tap2) * 0.8
        render_3d_spectrogram(synthetic_signal, sample_rate=48000, title="Synthetic 3D Double-Tap Dual Volcano Surface Mesh")
