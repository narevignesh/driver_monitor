import cv2
import mediapipe as mp
import numpy as np


mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=False,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
)

LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]
MOUTH_IDX = [78, 81, 13, 308, 14, 178]
HEAD_POSE_IDX = [1, 33, 263, 61, 291, 199]

EAR_THRESHOLD = 0.25
MAR_THRESHOLD = 0.6
CONSEC_FRAMES = 15

_drowsy_counter = 0
_yawn_counter = 0


def _distance(p1, p2):
    return float(np.linalg.norm(np.array(p1) - np.array(p2)))


def calculate_ear(eye_landmarks):
    v1 = _distance(eye_landmarks[1], eye_landmarks[5])
    v2 = _distance(eye_landmarks[2], eye_landmarks[4])
    h = _distance(eye_landmarks[0], eye_landmarks[3])
    return 0.0 if h == 0 else (v1 + v2) / (2.0 * h)


def calculate_mar(mouth_landmarks):
    v1 = _distance(mouth_landmarks[1], mouth_landmarks[5])
    v2 = _distance(mouth_landmarks[2], mouth_landmarks[4])
    h = _distance(mouth_landmarks[0], mouth_landmarks[3])
    return 0.0 if h == 0 else (v1 + v2) / (2.0 * h)


def estimate_head_pose(frame, landmarks):
    h, w = frame.shape[:2]
    image_points = np.array(
        [[landmarks[i][0], landmarks[i][1]] for i in HEAD_POSE_IDX], dtype=np.float64
    )
    model_points = np.array(
        [
            (0.0, 0.0, 0.0),
            (-30.0, -30.0, -30.0),
            (30.0, -30.0, -30.0),
            (-25.0, 30.0, -30.0),
            (25.0, 30.0, -30.0),
            (0.0, 65.0, -50.0),
        ],
        dtype=np.float64,
    )

    focal_length = w
    camera_matrix = np.array(
        [[focal_length, 0, w / 2], [0, focal_length, h / 2], [0, 0, 1]], dtype=np.float64
    )
    dist_coeffs = np.zeros((4, 1), dtype=np.float64)

    success, rotation_vector, _ = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE
    )
    if not success:
        return 0.0, 0.0, "NORMAL"

    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    angles, *_ = cv2.RQDecomp3x3(rotation_matrix)
    pitch = float(angles[0])
    yaw = float(angles[1])

    status = "DISTRACTED" if abs(yaw) > 25 or abs(pitch) > 20 else "NORMAL"
    return pitch, yaw, status


def extract_eye_regions(frame, landmarks):
    eye_points = [landmarks[i] for i in LEFT_EYE_IDX + RIGHT_EYE_IDX]
    xs = [p[0] for p in eye_points]
    ys = [p[1] for p in eye_points]
    x1, x2 = max(min(xs) - 10, 0), min(max(xs) + 10, frame.shape[1])
    y1, y2 = max(min(ys) - 10, 0), min(max(ys) + 10, frame.shape[0])
    return frame[y1:y2, x1:x2]


def extract_mouth_region(frame, landmarks):
    mouth_points = [landmarks[i] for i in MOUTH_IDX]
    xs = [p[0] for p in mouth_points]
    ys = [p[1] for p in mouth_points]
    x1, x2 = max(min(xs) - 10, 0), min(max(xs) + 10, frame.shape[1])
    y1, y2 = max(min(ys) - 10, 0), min(max(ys) + 10, frame.shape[0])
    return frame[y1:y2, x1:x2]


def detect_driver_state(frame):
    global _drowsy_counter, _yawn_counter

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = face_mesh.process(rgb_frame)

    ear = 0.0
    mar = 0.0
    drowsy = False
    yawning = False
    head_pose_status = "NORMAL"

    if result.multi_face_landmarks:
        h, w = frame.shape[:2]
        face_landmarks = result.multi_face_landmarks[0]
        landmarks = [
            (int(lm.x * w), int(lm.y * h))
            for lm in face_landmarks.landmark
        ]

        left_eye = [landmarks[i] for i in LEFT_EYE_IDX]
        right_eye = [landmarks[i] for i in RIGHT_EYE_IDX]
        mouth = [landmarks[i] for i in MOUTH_IDX]

        left_ear = calculate_ear(left_eye)
        right_ear = calculate_ear(right_eye)
        ear = (left_ear + right_ear) / 2.0
        mar = calculate_mar(mouth)

        _drowsy_counter = _drowsy_counter + 1 if ear < EAR_THRESHOLD else 0
        _yawn_counter = _yawn_counter + 1 if mar > MAR_THRESHOLD else 0

        drowsy = _drowsy_counter >= CONSEC_FRAMES
        yawning = _yawn_counter >= CONSEC_FRAMES

        _, _, head_pose_status = estimate_head_pose(frame, landmarks)
    else:
        _drowsy_counter = 0
        _yawn_counter = 0

    distracted = head_pose_status == "DISTRACTED"
    irregular = drowsy or yawning or distracted

    return {
        "ear": float(ear),
        "mar": float(mar),
        "drowsy": bool(drowsy),
        "yawning": bool(yawning),
        "head_pose_status": head_pose_status,
        "irregular": bool(irregular),
        "counter": int(max(_drowsy_counter, _yawn_counter)),
    }
