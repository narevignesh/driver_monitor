import time
import cv2
import numpy as np
import streamlit as st
import mediapipe as mp
import pandas as pd
import altair as alt
from utils import detect_driver_state

# Page Configuration
st.set_page_config(page_title="Pro Driver Monitor", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for Professional Look
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #262730;
        color: white;
        border: 1px solid #4B4B4B;
    }
    .stButton>button:hover {
        background-color: #FF4B4B;
        color: white;
        border: 1px solid #FF4B4B;
    }
    .metric-card {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #4B4B4B;
        margin-bottom: 10px;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .metric-label {
        font-size: 14px;
        color: #A0A0A0;
    }
    .status-alert {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .status-normal {
        background-color: #1E3A2F;
        color: #2ECC71;
        border: 1px solid #2ECC71;
    }
    .status-warning {
        background-color: #3A2F1E;
        color: #FFA500;
        border: 1px solid #FFA500;
    }
    .status-danger {
        background-color: #3A1E1E;
        color: #FF4B4B;
        border: 1px solid #FF4B4B;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🛡️ Professional Driver Monitoring System</h1>", unsafe_allow_html=True)

# Session State Initialization
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "irregular_action_count" not in st.session_state:
    st.session_state.irregular_action_count = 0
if "ear_history" not in st.session_state:
    st.session_state.ear_history = []
if "mar_history" not in st.session_state:
    st.session_state.mar_history = []

# Top Controls
c1, c2, c3 = st.columns([1, 1, 4])
with c1:
    if st.button("Start Camera"):
        st.session_state.camera_active = True
with c2:
    if st.button("Stop Camera"):
        st.session_state.camera_active = False

# Tabs logic
tab1, tab2 = st.tabs(["🎥 Monitor", "⚙️ Calibration"])

# --- Calibration Tab (Settings) ---
with tab2:
    st.markdown("### Sensitivity Settings")
    st.info("Adjust thresholds to match your environment and facial features.")
    
    col_cal1, col_cal2 = st.columns(2)
    with col_cal1:
        st.markdown("#### Drowsiness (EAR)")
        ear_thresh = st.slider(
            "Eye Aspect Ratio Threshold", 
            min_value=0.15, max_value=0.40, value=0.22, step=0.01,
            help="Lower value means eyes must be closed tighter to trigger."
        )
        st.caption(f"Current: **{ear_thresh}** (Default: 0.22)")

    with col_cal2:
        st.markdown("#### Yawning (MAR)")
        mar_thresh = st.slider(
            "Mouth Aspect Ratio Threshold", 
            min_value=0.50, max_value=1.20, value=0.75, step=0.05,
            help="Higher value means mouth must be wider open to trigger."
        )
        st.caption(f"Current: **{mar_thresh}** (Default: 0.75)")

    st.markdown("---")
    st.markdown("### 📖 Calibration Guide")
    
    guide_c1, guide_c2 = st.columns(2)
    with guide_c1:
        st.markdown("""
        **EAR (Drowsiness)**
        *Measures how open your eyes are.*
        - **Sensitive (0.25):** Triggers easily (even if eyes are slightly open).
        - **Balanced (0.22):** **Recommended.** Catches drowsy eyes accurately.
        - **Strict (0.20):** Hard to trigger (Eyes must be fully closed).
        """)
    with guide_c2:
        st.markdown("""
        **MAR (Yawning)**
        *Measures how wide your mouth is.*
        - **Sensitive (0.6 - 0.7):** Triggers easily (might catch talking).
        - **Balanced (0.75):** **Recommended.** Distinguishes yawning from talking.
        - **Strict (> 0.8):** Only triggers on deep, wide yawns.
        """)

# --- Monitor Tab (Main App) ---
with tab1:
    # Main Layout: 2 Columns
    col1, col2 = st.columns([1, 2]) # 1/3 Camera, 2/3 Report

    with col1:
        st.markdown("### 📷 Live Feed")
        frame_placeholder = st.empty()

    with col2:
        st.markdown("### 📊 Real-Time Telemetry")
        
        # Status Banner
        status_placeholder = st.empty()
        
        # Metrics Grid
        m1, m2, m3 = st.columns(3)
        with m1:
            ear_placeholder = st.empty()
        with m2:
            mar_placeholder = st.empty()
        with m3:
            head_placeholder = st.empty()
        
        st.markdown("### 📉 Analysis")
        chart_placeholder = st.empty()
        
        st.markdown("---")
        count_placeholder = st.empty()

    # Initial Static State
    if not st.session_state.camera_active:
        frame_placeholder.info("System Standby. Click 'Start Camera' to begin.")
        status_placeholder.markdown("""
            <div class="status-alert status-warning">
                SYSTEM OFF
            </div>
            """, unsafe_allow_html=True)
        count_placeholder.info(f"🚩 Total Irregular Events: **{st.session_state.irregular_action_count}**")

    # Main Loop - Only runs if active
    if st.session_state.camera_active:
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("Could not open webcam.")
            st.session_state.camera_active = False
        else:
            while st.session_state.camera_active:
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to read frame.")
                    break

                # Detection Logic - Passing Dynamic Thresholds
                state = detect_driver_state(frame, ear_threshold=ear_thresh, mar_threshold=mar_thresh)
                
                # Update Irregular Count
                if state["irregular"]:
                    st.session_state.irregular_action_count += 1

                # Update History for Charts
                st.session_state.ear_history.append(state["ear"])
                st.session_state.mar_history.append(state["mar"])
                
                # Keep only last 100 frames
                if len(st.session_state.ear_history) > 100:
                    st.session_state.ear_history.pop(0)
                if len(st.session_state.mar_history) > 100:
                    st.session_state.mar_history.pop(0)

                # --- Visuals on Frame (Minimal) ---
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(rgb, channels="RGB", use_container_width=True)

                # --- Dashboard Updates in Col 2 ---
                
                # Status Banner
                if state["irregular"]:
                    status_html = f"""
                    <div class="status-alert status-danger">
                        ⚠️ ALERT: IRREGULAR BEHAVIOR DETECTED
                    </div>
                    """
                else:
                    status_html = """
                    <div class="status-alert status-normal">
                        ✅ DRIVER STATUS: NORMAL
                    </div>
                    """
                status_placeholder.markdown(status_html, unsafe_allow_html=True)

                # Metrics
                ear_placeholder.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {'#FF4B4B' if state['drowsy'] else '#FAFAFA'}">{state['ear']:.2f} <span style="font-size: 14px; color: #888;">/ {ear_thresh}</span></div>
                    <div class="metric-label">EAR (Drowsiness)</div>
                </div>
                """, unsafe_allow_html=True)

                mar_placeholder.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {'#FF4B4B' if state['yawning'] else '#FAFAFA'}">{state['mar']:.2f} <span style="font-size: 14px; color: #888;">/ {mar_thresh}</span></div>
                    <div class="metric-label">MAR (Yawning)</div>
                </div>
                """, unsafe_allow_html=True)

                head_placeholder.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="color: {'#FF4B4B' if state['head_pose_status'] == 'DISTRACTED' else '#FAFAFA'}">{state['head_pose_status']}</div>
                    <div class="metric-label">Head Status</div>
                </div>
                """, unsafe_allow_html=True)

                # Charts with Threshold Lines
                df = pd.DataFrame({
                    "Frame": range(len(st.session_state.ear_history)),
                    "EAR": st.session_state.ear_history,
                    "MAR": st.session_state.mar_history
                })
                
                # EAR Chart
                ear_chart = alt.Chart(df).mark_line(color='#1f77b4').encode(
                    x='Frame',
                    y=alt.Y('EAR', scale=alt.Scale(domain=[0, 0.5]))
                )
                ear_rule = alt.Chart(pd.DataFrame({'y': [ear_thresh]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y')
                
                # MAR Chart
                mar_chart = alt.Chart(df).mark_line(color='#ff7f0e').encode(
                    x='Frame',
                    y=alt.Y('MAR', scale=alt.Scale(domain=[0, 1.5]))
                )
                mar_rule = alt.Chart(pd.DataFrame({'y': [mar_thresh]})).mark_rule(color='red', strokeDash=[5, 5]).encode(y='y')
                
                chart_placeholder.altair_chart((ear_chart + ear_rule) | (mar_chart + mar_rule), use_container_width=True)

                # Counter
                count_placeholder.info(f"🚩 Total Irregular Events: **{st.session_state.irregular_action_count}**")
                
                time.sleep(0.01) 
                
            cap.release()
