import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from tkinter import Tk, filedialog
import os
from collections import deque

# -------- Utilities --------
def lm_xy(lm, w, h):
    return (lm.x * w, lm.y * h)

# -------- Settings --------
PROC_W, PROC_H = 960, 540
Y_THRESHOLD = 15      # pixels for detecting lift-off / landing
SMOOTH_WINDOW = 5     # frames

# -------- File Selection --------
Tk().withdraw()
video_path = filedialog.askopenfilename(title="Select Video", filetypes=[("Video Files","*.mp4;*.avi;*.mov")])
if not video_path:
    exit()

filename = os.path.splitext(os.path.basename(video_path))[0]
output_folder = filename
os.makedirs(output_folder, exist_ok=True)
output_video_path = os.path.join(output_folder, f"{filename}_annotated.mp4")
csv_path = os.path.join(output_folder, f"{filename}_jump_log.csv")

# -------- Video Setup --------
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_vid = cv2.VideoWriter(output_video_path, fourcc, fps, (PROC_W, PROC_H))

# -------- MediaPipe --------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)
mp_draw = mp.solutions.drawing_utils

# -------- Jump Variables --------
state = 'grounded'
jumps = []
frame_idx = 0
air_start_time = None
takeoff_x = None
takeoff_y = None
ankle_y_history = deque(maxlen=SMOOTH_WINDOW)

# -------- Processing Loop --------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (PROC_W, PROC_H))
    frame_idx += 1
    t = frame_idx / fps

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    ankle_y = None
    ankle_x = None
    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        lm = results.pose_landmarks.landmark
        try:
            left_ankle = lm_xy(lm[mp_pose.PoseLandmark.LEFT_ANKLE], PROC_W, PROC_H)
            right_ankle = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_ANKLE], PROC_W, PROC_H)
            ankle_y = (left_ankle[1] + right_ankle[1]) / 2
            ankle_x = (left_ankle[0] + right_ankle[0]) / 2
            ankle_y_history.append(ankle_y)
        except:
            pass

    if ankle_y is not None and len(ankle_y_history) == SMOOTH_WINDOW:
        ankle_y_smooth = sum(ankle_y_history) / len(ankle_y_history)

        if state == 'grounded':
            # takeoff: sudden rise of ankles
            if ankle_y_history[0] - ankle_y_smooth > Y_THRESHOLD:
                state = 'airborne'
                air_start_time = t
                takeoff_x = ankle_x
                takeoff_y = ankle_y_smooth
        elif state == 'airborne':
            # landing: ankles come back down
            if ankle_y_smooth - min(ankle_y_history) > Y_THRESHOLD:
                state = 'grounded'
                air_time = t - air_start_time
                jump_distance = ankle_x - takeoff_x
                jumps.append({
                    'count': len(jumps)+1,
                    'takeoff_time': round(air_start_time,3),
                    'landing_time': round(t,3),
                    'air_time_s': round(air_time,3),
                    'jump_distance_px': round(jump_distance,2)
                })
                air_start_time = None
                takeoff_x = None
                takeoff_y = None

    # -------- Display --------
    if ankle_y is not None:
        cv2.putText(frame, f'Ankle Y: {int(ankle_y)}', (10,30), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
    cv2.putText(frame, f'Jumps: {len(jumps)}', (10,60), cv2.FONT_HERSHEY_SIMPLEX,0.9,(0,255,255),2)
    cv2.putText(frame, f'State: {state}', (10,95), cv2.FONT_HERSHEY_SIMPLEX,0.8,(200,200,0),2)
    cv2.putText(frame, f'Time: {t:.1f}s', (10,130), cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)

    cv2.imshow('Vertical Broad Jump Counter', frame)
    out_vid.write(frame)
    if cv2.waitKey(int(1000/fps)) & 0xFF in [27, ord('q')]:
        break

# -------- Cleanup --------
cap.release()
out_vid.release()
cv2.destroyAllWindows()
pose.close()

# -------- Save CSV --------
if jumps:
    pd.DataFrame(jumps).to_csv(csv_path, index=False)
    print(f"Saved {csv_path} with {len(jumps)} jumps.")
else:
    print("No jumps detected.")
