# 🛡️ Advanced Driver Monitoring System - Project Overview

**GitHub Repository:** [https://github.com/narevignesh/driver_monitor](https://github.com/narevignesh/driver_monitor.git)

## 1. Project Overview
**Project Type:** Deep Learning & Computer Vision Application

### Problem Statement
Driver fatigue and distraction are among the leading causes of severe road accidents worldwide. Traditional vehicles lack continuous, real-time monitoring of the driver's cognitive state, leading to delayed responses to drowsiness or visual distraction.

### Proposed Solution
A real-time, lightweight **Deep Learning (DL) based Driver Monitoring System**. This system actively tracks facial topography, eye closure (detecting microsleeps), yawning patterns, and dynamic head pose (detecting distraction) to provide instant visual and auditory alerts before critical incidents occur.

### Technical Approach
The project utilizes advanced computer vision and geometric calculations built on top of robust deep learning models. By extracting 3D facial landmarks in real-time, the system continuously calculates the **Eye Aspect Ratio (EAR)** and **Mouth Aspect Ratio (MAR)**. This approach avoids the massive computational overhead of running heavy CNNs on every frame, allowing for stable, high-FPS performance even on standard CPU hardware.

---

## 2. Deep Learning Details

This is a **Deep Learning (DL) project** that leverages state-of-the-art pre-trained neural networks optimized for edge computing and real-time inference.

### Algorithms Used
- **Convolutional Neural Networks (CNNs):** The architectural foundation of the facial feature extraction.
- **BlazeFace Algorithm:** An extremely fast and lightweight face detector used to crop the face from the larger video frame.
- **Attention Mesh Networks:** A 3D facial landmark predictor that estimates 468 precise coordinates on the face using a coordinate regression deep neural network.

### Pre-trained Models
Instead of training a model from scratch, this system utilizes **Google's MediaPipe Face Mesh**, a highly optimized, pre-trained deep learning pipeline. It encapsulates complex TensorFlow Lite models that deliver sub-millisecond inference times. The pipeline consists of two primary models working in tandem:
1. **Face Detection Model:** Computes bounding boxes around faces.
2. **Face Landmark Model:** Predicts the 3D geometry of the face from the cropped bounding box.

### Dataset Used (Training Background)
The underlying deep learning models were trained by Google engineers on a massive, proprietary dataset containing over **30,000 highly diverse facial images**. This dataset included varied lighting conditions, extreme head poses, and diverse ethnicities to ensure the model exhibits robust fairness, accuracy, and generalization in real-world driving environments.

---

## 3. Technology Stack & Tools Used

### Core Deep Learning & Computer Vision
- **MediaPipe:** The primary Deep Learning framework utilized for complex face mesh and landmark detection.
- **OpenCV (cv2):** Used for hardware video capture, color space conversions, and drawing metric overlays directly onto the video feed.

### Frontend, Data processing & UI
- **Python (v3.10+):** The primary programming language.
- **Streamlit:** A powerful Python framework used to rapidly build the interactive telemetry dashboard, manage UI state, and render real-time video without browser lag.
- **NumPy & Pandas:** Utilized for high-speed mathematical array operations and buffering temporal data for charts.
- **Altair:** A declarative statistical visualization library used for rendering the live EAR and MAR charts.

---

## 4. Key Performance Metrics

1. **Drowsiness (EAR):** Tracks the distance between the upper and lower eyelids. When the EAR falls below a strict threshold (e.g., `< 0.22`) for consecutive frames, the driver is flagged as asleep.
2. **Yawning (MAR):** Tracks the vertical distance of the mouth. Frequent instances (e.g., `MAR > 0.75`) serve as an early warning for fatigue before actual sleep occurs.
3. **Distraction (Head Pose Estimation):** Utilizes the 3D coordinates (x, y, z) of the nose and jawline to project pitch, yaw, and roll calculations—ensuring the driver's eyes remain strictly on the road.

---

## 5. System Architecture
1. **Input:** Live webcam/camera feed.
2. **Pipeline:** OpenCV processes frame -> MediaPipe Deep Learning model infers 468 landmarks -> Python logic computes EAR/MAR and Head Pose -> Streamlit updates UI metrics.
3. **Output:** Live annotated video feed, dynamic data charts, and real-time system alerts.
