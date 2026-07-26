import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
import pickle
from scipy.io import wavfile

from utils import DATASET_DIR, SAMPLE_RATE, WINDOW_SIZE, extract_2d_spectrogram

st.set_page_config(
    page_title="MORSE - Acoustic AI Research Workbench",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ MORSE - Acoustic AI & Physical Computing Research Workbench")
st.markdown("### Software-Defined Unibody Spatial Tap Engine — Experimentation & Feature Explorer")

# Tabs
tab1, tab2, tab3 = st.tabs(["📊 3D Feature Space Explorer", "🧪 Hypothesis & Experiment Tree", "⚙️ Active Calibrated DSP Bounds"])

@st.cache_data
def load_dataset_features():
    categories = ["left_palm_rest", "right_palm_rest", "palm_resting", "typing", "noise", "desk_tap"]
    data = []
    
    for cat in categories:
        cat_dir = os.path.join(DATASET_DIR, cat)
        if not os.path.exists(cat_dir):
            continue
        files = [f for f in os.listdir(cat_dir) if f.endswith(".npy") or f.endswith(".wav")][:50] # Sample up to 50 per class for speed
        
        for f_name in files:
            f_path = os.path.join(cat_dir, f_name)
            if f_name.endswith(".npy"):
                sig = np.load(f_path)
            else:
                sr, sig = wavfile.read(f_path)
                sig = sig.astype(np.float32) / 32768.0

            sig = sig.flatten()
            vol = np.linalg.norm(sig) * 10
            
            if len(sig) < WINDOW_SIZE:
                buffer_history = np.pad(sig, (0, WINDOW_SIZE - len(sig)))
            else:
                buffer_history = sig[-WINDOW_SIZE:]

            peak_idx = np.argmax(np.abs(buffer_history))
            start_idx = max(0, peak_idx - 100)
            end_idx = min(len(buffer_history), peak_idx + 1000)
            transient = buffer_history[start_idx:end_idx]

            fft_vals = np.abs(np.fft.rfft(transient))
            freqs = np.fft.rfftfreq(len(transient), d=1.0/SAMPLE_RATE)

            rms = np.sqrt(np.mean(transient**2)) + 1e-6
            peak = np.max(np.abs(transient))
            crest_factor = peak / rms

            hp_energy = np.sum(fft_vals[freqs >= 2500]) + 1e-6
            total_fft_energy = np.sum(fft_vals) + 1e-6
            hp_ratio = hp_energy / total_fft_energy
            centroid = np.sum(freqs * fft_vals) / (total_fft_energy + 1e-6)

            data.append({
                "Category": cat,
                "Volume": vol,
                "Crest Factor": crest_factor,
                "HP Ratio": hp_ratio,
                "Centroid (Hz)": centroid,
                "Sample": f_name
            })
            
    return pd.DataFrame(data)

df = load_dataset_features()

with tab1:
    st.subheader("🌋 3D Acoustic Feature Space Scatter")
    st.markdown("Visualizing physical separation across **Volume**, **Crest Factor**, and **High-Pass (HP) Ratio**.")
    
    if not df.empty:
        col_x, col_y, col_z = st.columns(3)
        with col_x:
            x_axis = st.selectbox("X-Axis", ["HP Ratio", "Crest Factor", "Volume", "Centroid (Hz)"], index=0)
        with col_y:
            y_axis = st.selectbox("Y-Axis", ["Crest Factor", "HP Ratio", "Volume", "Centroid (Hz)"], index=0)
        with col_z:
            z_axis = st.selectbox("Z-Axis", ["Volume", "HP Ratio", "Crest Factor", "Centroid (Hz)"], index=0)

        fig = px.scatter_3d(
            df,
            x=x_axis,
            y=y_axis,
            z=z_axis,
            color="Category",
            symbol="Category",
            hover_data=["Sample", "Centroid (Hz)"],
            height=650,
            opacity=0.85
        )
        fig.update_layout(margin=dict(l=0, r=0, b=0, t=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No dataset samples found in 'dataset/' directory.")

with tab2:
    st.subheader("🧪 Research Experiment & Hypothesis Tracker")
    st.markdown("Clear historical view of what we hypothesized, what worked, what failed, and what is left to try.")
    
    experiments = [
        {"ID": "EXP-01", "Hypothesis": "Dual-Mic TDOA & Amplitude Ratio Localization", "Category": "Hardware Physics", "Status": "✅ PASSED", "Result": "Proved 16x amplitude ratio gap between Left/Right mics."},
        {"ID": "EXP-02", "Hypothesis": "Single-Mic Unibody Chassis Volume Step Function", "Category": "Hardware Physics", "Status": "✅ PASSED", "Result": "Discovered 2:1 volume step function (Left Vol >= 8.5 vs Right Vol <= 9.2)."},
        {"ID": "EXP-03", "Hypothesis": "1D FFT Spectral Model Classification", "Category": "ML Model", "Status": "⚠️ PARTIAL", "Result": "Worked for loud taps, but struggled with soft right tap overlap."},
        {"ID": "EXP-04", "Hypothesis": "2D STFT Spectrogram + HistGradientBoosting", "Category": "ML Model", "Status": "✅ PASSED", "Result": "Achieved 99.2% cross-validation accuracy across 6 categories."},
        {"ID": "EXP-05", "Hypothesis": "Empirical DSP Gating (Crest Factor >= 1.6, HP >= 0.05)", "Category": "DSP Filter", "Status": "✅ PASSED", "Result": "Completely eliminated wrist slide & desk thud false positives."},
        {"ID": "EXP-06", "Hypothesis": "3D STFT Spectrogram Surface Topography Prominence", "Category": "Computer Vision", "Status": "⏳ QUEUED", "Result": "Next to test: Detect double-taps using 3D dual-peak surface mesh."},
        {"ID": "EXP-07", "Hypothesis": "Adaptive Environmental Noise Floor Auto-Calibration", "Category": "DSP Filter", "Status": "⏳ QUEUED", "Result": "Next to test: 3-second noise profiling wizard on startup."}
    ]
    
    exp_df = pd.DataFrame(experiments)
    st.dataframe(exp_df, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("⚙️ Locked Physical Dynamic Bounds (`smart_detector.py`)")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Volume Floor", "3.5 RMS", "Noise Cutoff")
    col2.metric("Volume Ceiling", "110.0 RMS", "Slam Bound")
    col3.metric("Min Crest Factor", "1.60", "Rub Rejection")
    col4.metric("Min HP Ratio", "0.05", "Right Tap Attenuation")

    st.code("""
# Active Stage 1 DSP Candidate Filter
is_dsp_candidate = (
    (volume >= 3.5) and 
    (volume <= 110.0) and 
    (crest_factor >= 1.60) and 
    (hp_ratio >= 0.05 or pre_surge_ratio >= min_pre_surge)
)
""", language="python")
