# Advanced Driver Monitor

A minimal real-time driver monitoring project built with Streamlit, OpenCV, MediaPipe, and TensorFlow.

## Setup

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
streamlit run app.py
```

## Features

- EAR drowsiness detection
- MAR yawning detection
- Head pose distraction detection
- Real-time alerts
- Recording support

## Behavior

- Real-time webcam only
- Detect eye closure
- Detect yawning
- Detect head turn / head down
- Show live metrics
- Allow recording
