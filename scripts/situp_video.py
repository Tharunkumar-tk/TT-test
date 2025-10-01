import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from tkinter import Tk, filedialog
from collections import deque
import os

# -------- Utilities --------
def angle(a, b, c):
    ba = np.array([a[0]-b[0], a[1]-b[1]])
    bc = np.array([c[0]-b[0], c[1]-b[1]])
    cosang = np.clip(np.dot(ba, bc) / ((np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-9), -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))

def lm_xy(lm, w, h):
    return (lm.x * w, lm.y * h)

# -------- Settings --------
PROC_W, PROC_H = 960, 540   # ✅ fixed resolution for full view
MIN_DIP_CHANGE = 15

# -------- File Selection --------
Tk().withdraw()
video_path = filedialog.askopenfilename(title="Select Video", filetypes=[("Video Files","*.mp4;*.avi;*.mov")])
if not video_path:
    exit()

filename = os.path.splitext(os.path.basename(video_path))[0]
output_folder = filename
os.makedirs(output_folder, exist_ok=True)
output_video_path = os.path.join(output_folder, f"{filename}_annotated.mp4")
csv_path = os.path.join(output_folder, f"{filename}_situp_log.csv")

# -------- Video Setup --------
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_vid = cv2.VideoWriter(output_video_path, fourcc, fps, (PROC_W, PROC_H))

# -------- MediaPipe --------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)
mp_draw = mp.solutions.drawing_utils

# -------- Sit-up Variables --------
angle_history = deque(maxlen=5)
state = 'up'
reps = []
last_extreme_angle = None
dip_start_time = None
frame_idx = 0

# -------- Processing Loop --------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ✅ resize for consistent analysis
    frame = cv2.resize(frame, (PROC_W, PROC_H))

    frame_idx += 1
    t = frame_idx / fps

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    elbow_angle = None
    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        lm = results.pose_landmarks.landmark
        try:
            ls = lm_xy(lm[mp_pose.PoseLandmark.LEFT_SHOULDER], PROC_W, PROC_H)
            le = lm_xy(lm[mp_pose.PoseLandmark.LEFT_ELBOW], PROC_W, PROC_H)
            lw = lm_xy(lm[mp_pose.PoseLandmark.LEFT_WRIST], PROC_W, PROC_H)
            rs = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_SHOULDER], PROC_W, PROC_H)
            re = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_ELBOW], PROC_W, PROC_H)
            rw = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_WRIST], PROC_W, PROC_H)
            elbow_angle = (angle(ls, le, lw) + angle(rs, re, rw)) / 2
        except:
            pass

    # -------- Rep Counting --------
    if elbow_angle is not None:
        angle_history.append(elbow_angle)
        elbow_angle_sm = sum(angle_history) / len(angle_history)

        if last_extreme_angle is None:
            last_extreme_angle = elbow_angle_sm

        if state == 'up' and last_extreme_angle - elbow_angle_sm >= MIN_DIP_CHANGE:
            state = 'down'
            dip_start_time = t
            last_extreme_angle = elbow_angle_sm

        elif state == 'down' and elbow_angle_sm - last_extreme_angle >= MIN_DIP_CHANGE:
            state = 'up'
            rep = {
                'count': len(reps) + 1,
                'down_time': round(dip_start_time, 3) if dip_start_time else 0,
                'up_time': round(t, 3),
                'angle_change': round(elbow_angle_sm - last_extreme_angle, 2)
            }
            reps.append(rep)
            dip_start_time = None
            last_extreme_angle = elbow_angle_sm

    # -------- Dip Timer --------
    dip_time_display = (t - dip_start_time) if state == 'down' and dip_start_time else 0.0

    # -------- Display --------
    if elbow_angle is not None:
        cv2.putText(frame, f'Elbow: {int(elbow_angle_sm)}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, f'Sit-ups: {len(reps)}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    cv2.putText(frame, f'State: {state}', (10, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 0), 2)
    cv2.putText(frame, f'Dip: {dip_time_display:.3f}s', (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
    cv2.putText(frame, f'Time: {t:.1f}s', (10, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow('Sit-up Counter', frame)
    out_vid.write(frame)
    if cv2.waitKey(int(1000 / fps)) & 0xFF in [27, ord('q')]:
        break

# -------- Cleanup --------
cap.release()
out_vid.release()
cv2.destroyAllWindows()
pose.close()

# -------- Save CSV --------
if reps:
    pd.DataFrame(reps).to_csv(csv_path, index=False)
    print(f"Saved {csv_path} with {len(reps)} reps.")
else:
    print("No reps detected.")
