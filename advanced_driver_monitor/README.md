# 🛡️ Professional Driver Monitoring System

A lightweight, real-time driver monitoring application built with **Streamlit**, **OpenCV**, and **MediaPipe**. This system detects drowsiness, yawning, and distractions to ensure driver safety.

---

## 🚀 Features
- **EAR Drowsiness Detection**: Real-time eye closure analysis.
- **MAR Yawning Detection**: Detects excessive yawning.
- **Head Pose Estimation**: Identifies when the driver is looking away from the road.
- **Live Analysis Dashboard**: Real-time line charts visualize EAR and MAR trends.
- **Dynamic Calibration**: Adjust sensitivity thresholds directly in the UI.
- **Professional 2-Column UI**: Designed for easy monitoring and telemetry reading.

---

## � System Requirements & Compatibility
To ensure stability, the project is tested and optimized for the following environment:

- **Python**: `v3.10.x` (Recommended: `3.10.6`)
- **Core Libraries**:
    - `streamlit`: `v1.30.0` or higher
    - `mediapipe`: `v0.10.9` (**Strict Requirement** for stability)
    - `protobuf`: `< 4.0.0` (Recommended: `3.20.3` to prevent crashes)
    - `opencv-python`: `v4.8.x` or higher
    - `pandas`: `v2.x`
    - `altair`: `v5.x` or `v6.x`

---

## �🛠️ Installation

1. **Clone the Project**
2. **Setup Virtual Environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

---

## 📖 User Manual

### 1. Starting the Monitor
- Launch the app and go to the **🎥 Monitor** tab.
- Click **"Start Camera"** at the top.
- The system will begin analyzing your face landmarks instantly.

### 2. Monitoring Metrics
- **EAR (Eye Aspect Ratio)**: Shows how open your eyes are.
- **MAR (Mouth Aspect Ratio)**: Shows how wide your mouth is.
- **Analysis Chart**: Watch the trends to see your baseline values.

### 3. Calibration (Customizing Sensitivity)
If the app is too sensitive or not sensitive enough, go to the **⚙️ Calibration** tab:
- **EAR Slider**: Move left for stricter (harder to trigger) or right for sensitive.
- **MAR Slider**: Move right for stricter (ignores talking) or left for sensitive.

---

## ⚙️ Technical Details (Thresholds & Timing)

The system uses specific mathematical thresholds to determine "Irregular Behavior".

### EAR (Drowsiness)
- **Standard Threshold**: `0.22` (Customizable).
- **Trigger Logic**: If eyes are closed (EAR < Threshold) for **40 consecutive frames** (~1.5 to 2 seconds), a Drowsy Alert is triggered.
- **Sensitivity Guide**:
    - **Sensitive (0.25):** Good for low-light or far cameras.
    - **Strict (0.20):** Only triggers on total eye closure.

### MAR (Yawning)
- **Standard Threshold**: `0.75` (Customizable).
- **Trigger Logic**: If mouth is open wide (MAR > Threshold) for **40 consecutive frames** (~1.5 to 2 seconds), a Yawning Alert is triggered.
- **Sensitivity Guide**:
    - **Sensitive (0.6):** Might catch talking or singing.
    - **Strict (0.8+):** Only catches very wide yawning.

### Head Pose (Distraction)
- **Logic**: Calculates Yaw (side-side) and Pitch (up-down) angles.
- **Trigger**: "Distracted" status appears if:
    - **Yaw > 35°** (Looking far left or right).
    - **Pitch > 25°** (Looking far up or down at a phone).

---

## 📦 Dependencies
- `streamlit`
- `opencv-python`
- `mediapipe` (v0.10.9)
- `pandas`
- `altair`

*Note: This system is built to be lightweight and does not require TensorFlow or PyTorch.*
