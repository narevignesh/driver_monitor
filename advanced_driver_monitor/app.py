import os
import time

import cv2
import streamlit as st

from utils import detect_driver_state


st.set_page_config(page_title="Advanced Driver Monitor", layout="wide")
st.title("Advanced Real-Time Driver Monitoring System")

if "camera_running" not in st.session_state:
    st.session_state.camera_running = False
if "recording" not in st.session_state:
    st.session_state.recording = False
if "irregular_action_count" not in st.session_state:
    st.session_state.irregular_action_count = 0
if "camera" not in st.session_state:
    st.session_state.camera = None
if "writer" not in st.session_state:
    st.session_state.writer = None

col1, col2, col3, col4 = st.columns(4)
if col1.button("Start Camera"):
    st.session_state.camera_running = True
if col2.button("Stop Camera"):
    st.session_state.camera_running = False
    if st.session_state.camera is not None:
        st.session_state.camera.release()
        st.session_state.camera = None
    if st.session_state.writer is not None:
        st.session_state.writer.release()
        st.session_state.writer = None
    st.session_state.recording = False
if col3.button("Start Recording"):
    st.session_state.recording = True
if col4.button("Stop Recording"):
    st.session_state.recording = False
    if st.session_state.writer is not None:
        st.session_state.writer.release()
        st.session_state.writer = None

frame_placeholder = st.empty()
status_placeholder = st.empty()

if st.session_state.camera_running:
    if st.session_state.camera is None:
        st.session_state.camera = cv2.VideoCapture(0)

    while st.session_state.camera_running:
        ret, frame = st.session_state.camera.read()
        if not ret:
            status_placeholder.error("Could not read from webcam.")
            break

        state = detect_driver_state(frame)
        status_text = "ALERT" if state["irregular"] else "NORMAL"

        if state["irregular"]:
            st.session_state.irregular_action_count += 1

        cv2.putText(frame, f"EAR: {state['ear']:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"MAR: {state['mar']:.2f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"Status: {status_text}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255) if state['irregular'] else (0, 255, 0), 2)
        cv2.putText(frame, f"Head Pose: {state['head_pose_status']}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
        cv2.putText(frame, f"Counter: {state['counter']}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)

        if st.session_state.recording:
            os.makedirs("recordings", exist_ok=True)
            if st.session_state.writer is None:
                h, w = frame.shape[:2]
                fourcc = cv2.VideoWriter_fourcc(*"XVID")
                st.session_state.writer = cv2.VideoWriter("recordings/output.avi", fourcc, 20.0, (w, h))
            st.session_state.writer.write(frame)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(rgb, channels="RGB", use_container_width=True)

        if state["irregular"]:
            status_placeholder.error("⚠️ Warning: Irregular driver behavior detected!")
        else:
            status_placeholder.success("Driver status is normal.")

        st.write(f"EAR: {state['ear']:.3f}")
        st.write(f"MAR: {state['mar']:.3f}")
        st.write(f"Drowsy: {state['drowsy']}")
        st.write(f"Yawning: {state['yawning']}")
        st.write(f"Head pose: {state['head_pose_status']}")
        st.write(f"Irregular action count: {st.session_state.irregular_action_count}")

        time.sleep(0.03)
        st.rerun()

if not st.session_state.camera_running:
    st.info("Click 'Start Camera' to begin monitoring.")
