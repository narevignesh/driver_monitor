import time
import cv2
import numpy as np
import streamlit as st
import mediapipe as mp
import pandas as pd
import altair as alt
import base64
from utils import detect_driver_state, reset_counters

# Page Configuration
st.set_page_config(page_title="Pro Driver Monitor", layout="wide", initial_sidebar_state="collapsed")

@st.cache_resource
def get_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return None
    return cap

# Simple beep sound base64 (Short clear beep)
BEEP_B64 = "data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU9vT19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19fX19f"

def play_alarm():
    # Display the alarm audio only if it's not already playing or just play once
    # We use a placeholder to avoid cluttering the DOM
    if "alarm_placeholder" not in st.session_state:
        st.session_state.alarm_placeholder = st.empty()
    
    md = f'<audio autoplay="true"><source src="{BEEP_B64}" type="audio/wav"></audio>'
    st.session_state.alarm_placeholder.markdown(md, unsafe_allow_html=True)


def handle_stop_alarm():
    st.session_state.alarm_triggered = False
    st.session_state.irregular_action_count = 0
    reset_counters()
    if "alarm_placeholder" in st.session_state:
        st.session_state.alarm_placeholder.empty()

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; border: 1px solid #4B4B4B; }
    .stButton>button:hover { background-color: #FF4B4B; color: white; border: 1px solid #FF4B4B; }
    .metric-card { background-color: #262730; padding: 15px; border-radius: 10px; border: 1px solid #4B4B4B; margin-bottom: 10px; text-align: center; }
    .metric-value { font-size: 24px; font-weight: bold; }
    .metric-label { font-size: 14px; color: #A0A0A0; }
    .status-alert { padding: 20px; border-radius: 10px; text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px; }
    .status-normal { background-color: #1E3A2F; color: #2ECC71; border: 1px solid #2ECC71; }
    .status-warning { background-color: #3A2F1E; color: #FFA500; border: 1px solid #FFA500; }
    .status-danger { background-color: #3A1E1E; color: #FF4B4B; border: 1px solid #FF4B4B; }
    .alarm-active { background-color: #FF0000; color: white; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0.5; } }
    </style>
    """, unsafe_allow_html=True)

# Title
st.markdown("<h1 style='text-align: center; margin-bottom: 20px;'>🛡️ Driver Monitoring System</h1>", unsafe_allow_html=True)

# Session State Initialization
if "camera_active" not in st.session_state:
    st.session_state.camera_active = False
if "alarm_triggered" not in st.session_state:
    st.session_state.alarm_triggered = False
if "irregular_action_count" not in st.session_state:
    st.session_state.irregular_action_count = 0
if "ear_history" not in st.session_state:
    st.session_state.ear_history = []
if "mar_history" not in st.session_state:
    st.session_state.mar_history = []

# Top Controls
c1, c2, c3, c4 = st.columns([1, 1, 1, 3])
with c1:
    if st.button("Start Camera"):
        st.session_state.camera_active = True
with c2:
    if st.button("Stop Camera"):
        st.session_state.camera_active = False
        st.cache_resource.clear() # Force close camera hardware on stop
with c3:
    st.button("🚨 Stop Alarm", on_click=handle_stop_alarm)

# Tabs logic
tab1, tab2 = st.tabs(["🎥 Monitor", "⚙️ Calibration"])

# --- Calibration Tab (Settings) ---
with tab2:
    st.markdown("### Sensitivity & Alarm Settings")
    st.info("Fine-tune thresholds, detection timing, and alarm limits.")
    
    col_cal1, col_cal2 = st.columns(2)
    with col_cal1:
        st.markdown("#### 👁️ Detection Logic")
        ear_thresh = st.slider("EAR Threshold", 0.15, 0.40, 0.22, 0.01)
        mar_thresh = st.slider("MAR Threshold", 0.50, 1.20, 0.75, 0.05)
        det_seconds = st.slider("Detection Duration (Seconds)", 0.5, 5.0, 1.5, 0.1, help="Time action must persist to trigger alert.")

    with col_cal2:
        st.markdown("#### 🔔 Alarm Trigger")
        alarm_limit = st.slider("Alarm Event Limit", 10, 3000, 500, 10, help="Total events before main alarm triggers.")
        st.write(f"Current Count: **{st.session_state.irregular_action_count}** / {alarm_limit}")

    st.markdown("---")
    st.markdown("### 📖 Comprehensive Calibration Guide")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("""
        #### 👁️ Drowsiness (EAR)
        - **Sensitive (0.25)**: Easier to trigger; use if the camera is far.
        - **Balanced (0.22)**: Recommended for most drivers.
        - **Strict (0.20)**: Best for high-light/glare environments.
        
        #### ⏱️ Duration (Seconds)
        - Action must persist for this time to trigger an alert.
        - **1.5s** is balanced; lower for faster (stricter) detection.
        """)
    with g2:
        st.markdown("""
        #### 👄 Yawning (MAR)
        - **Sensitive (0.60)**: Triggers on deep breathing/talking.
        - **Balanced (0.75)**: Recommended for clear yawns.
        - **Strict (0.90+)**: Ignores heavy talking.
        
        #### 🔔 Alarm Event Limit
        - Once **Total Events** hit this limit, the system alarm stays **ON**.
        - Set to **500-1000** for long drives; lower for testing.
        """)
    
    st.markdown("---")
    st.markdown("### 🛡️ About Driver Monitor System")
    st.markdown("""
    This system is an advanced AI-powered safety assistant designed to reduce accidents caused by driver fatigue and distraction. 
    It uses computer vision to analyze facial landmarks in real-time.
    
    **How it works:**
    1. **Fatigue Tracking**: Monitors EAR (Eyes) and MAR (Mouth) to detect signs of sleepiness.
    2. **Distraction Check**: Uses head-pose estimation to ensure you are looking at the road.
    3. **Persistent Alerts**: Keeps you focused with visual warnings and a final system alarm if irregular behavior persists.
    
    *Built with MediaPipe & Streamlit for a lightweight, high-performance experience.*
    """)

# --- Monitor Tab (Main App) ---
with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 📷 Live Feed")
        frame_placeholder = st.empty()
    with col2:
        st.markdown("### 📊 Real-Time Telemetry")
        status_placeholder = st.empty()
        m1, m2, m3 = st.columns(3)
        with m1: ear_placeholder = st.empty()
        with m2: mar_placeholder = st.empty()
        with m3: head_placeholder = st.empty()
        st.markdown("### 📉 Analysis")
        chart_placeholder = st.empty()
        st.markdown("---")
        count_placeholder = st.empty()

    if not st.session_state.camera_active:
        frame_placeholder.info("System Standby. Click 'Start Camera' to begin.")
        status_placeholder.markdown('<div class="status-alert status-warning">SYSTEM OFF</div>', unsafe_allow_html=True)
        count_placeholder.info(f"🚩 Total Irregular Events: **{st.session_state.irregular_action_count}**")

    if st.session_state.camera_active:
        # FPS Estimation (Assuming ~20 FPS for slider conversion)
        consec_frames = int(det_seconds * 20)
        
        cap = get_camera()
        if cap is None:
            st.error("Could not open webcam.")
            st.session_state.camera_active = False
        else:
            while st.session_state.camera_active:
                ret, frame = cap.read()
                if not ret: break

                state = detect_driver_state(frame, ear_threshold=ear_thresh, mar_threshold=mar_thresh, consec_frames=consec_frames)
                
                if state["irregular"]:
                    st.session_state.irregular_action_count += 1
                
                # Check Alarm Limit
                if st.session_state.irregular_action_count >= alarm_limit:
                    st.session_state.alarm_triggered = True

                # Update Histories
                st.session_state.ear_history.append(state["ear"])
                st.session_state.mar_history.append(state["mar"])
                if len(st.session_state.ear_history) > 100:
                    st.session_state.ear_history.pop(0)
                    st.session_state.mar_history.pop(0)

                # Feed Update
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_placeholder.image(rgb, channels="RGB", use_container_width=True)

                # Status & Alarm
                if st.session_state.alarm_triggered:
                    play_alarm() # Plays browser beep
                    status_html = '<div class="status-alert alarm-active">🚨 CRITICAL: STOP DRIVING - ALARM ACTIVE 🚨</div>'
                elif state["irregular"]:
                    status_html = '<div class="status-alert status-danger">⚠️ ALERT: IRREGULAR BEHAVIOR</div>'
                else:
                    status_html = '<div class="status-alert status-normal">✅ DRIVER STATUS: NORMAL</div>'
                
                status_placeholder.markdown(status_html, unsafe_allow_html=True)

                # Metrics
                ear_placeholder.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {"#FF4B4B" if state["drowsy"] else "#FAFAFA"}">{state["ear"]:.2f} <span style="font-size:14px;color:#888;">/{ear_thresh}</span></div><div class="metric-label">EAR</div></div>', unsafe_allow_html=True)
                mar_placeholder.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {"#FF4B4B" if state["yawning"] else "#FAFAFA"}">{state["mar"]:.2f} <span style="font-size:14px;color:#888;">/{mar_thresh}</span></div><div class="metric-label">MAR</div></div>', unsafe_allow_html=True)
                head_placeholder.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {"#FF4B4B" if state["head_pose_status"]=="DISTRACTED" else "#FAFAFA"}">{state["head_pose_status"]}</div><div class="metric-label">Head</div></div>', unsafe_allow_html=True)

                # Charts
                df = pd.DataFrame({"Frame": range(len(st.session_state.ear_history)), "EAR": st.session_state.ear_history, "MAR": st.session_state.mar_history})
                e_c = alt.Chart(df).mark_line(color='#1f77b4').encode(x='Frame', y=alt.Y('EAR', scale=alt.Scale(domain=[0,0.5])))
                e_r = alt.Chart(pd.DataFrame({'y':[ear_thresh]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='y')
                m_c = alt.Chart(df).mark_line(color='#ff7f0e').encode(x='Frame', y=alt.Y('MAR', scale=alt.Scale(domain=[0,1.5])))
                m_r = alt.Chart(pd.DataFrame({'y':[mar_thresh]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='y')
                chart_placeholder.altair_chart((e_c + e_r) | (m_c + m_r), use_container_width=True)

                count_placeholder.info(f"🚩 Total Events: **{st.session_state.irregular_action_count}** / {alarm_limit}")
                time.sleep(0.01)
            # Do NOT cap.release() here to keep it cached for restarts
            # Hardware is released only when st.cache_resource.clear() is called in Stop button
