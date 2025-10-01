import cv2
import mediapipe as mp
import numpy as np
import pandas as pd
from collections import deque
import os
import sys

def angle(a, b, c):
    ba = np.array([a[0]-b[0], a[1]-b[1]])
    bc = np.array([c[0]-b[0], c[1]-b[1]])
    cosang = np.clip(np.dot(ba, bc) / ((np.linalg.norm(ba)*np.linalg.norm(bc))+1e-9), -1.0, 1.0)
    return float(np.degrees(np.arccos(cosang)))

def lm_xy(lm, w, h):
    return (lm.x * w, lm.y * h)

video_path = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('VIDEO_PATH')
if not video_path or not os.path.exists(video_path):
    print(f"Error: Video file not found: {video_path}")
    sys.exit(1)

cap = cv2.VideoCapture(video_path)
filename = os.path.splitext(os.path.basename(video_path))[0]
output_folder = os.path.join(os.path.dirname(video_path), filename)
os.makedirs(output_folder, exist_ok=True)
output_video_path = os.path.join(output_folder, f"{filename}_annotated.mp4")

fps = cap.get(cv2.CAP_PROP_FPS) or 30
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_vid = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)
mp_draw = mp.solutions.drawing_utils

DOWN_ANGLE = 75
UP_ANGLE = 110
MIN_DIP_DURATION = 0.2
SMOOTH_N = 3

angle_history = deque(maxlen=SMOOTH_N)
state = 'up'
in_dip = False
dip_start_time = None
current_dip_min_angle = 180
reps = []

frame_idx = 0
PROCESS_SCALE = 0.5

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_idx += 1
    t = frame_idx / fps

    small_frame = cv2.resize(frame, (0,0), fx=PROCESS_SCALE, fy=PROCESS_SCALE)
    img_rgb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    elbow_angle = None
    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        lm = results.pose_landmarks.landmark
        try:
            ls = lm_xy(lm[mp_pose.PoseLandmark.LEFT_SHOULDER], width, height)
            le = lm_xy(lm[mp_pose.PoseLandmark.LEFT_ELBOW], width, height)
            lw = lm_xy(lm[mp_pose.PoseLandmark.LEFT_WRIST], width, height)
            rs = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_SHOULDER], width, height)
            re = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_ELBOW], width, height)
            rw = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_WRIST], width, height)
            ang_l = angle(ls, le, lw)
            ang_r = angle(rs, re, rw)
            elbow_angle = (ang_l + ang_r)/2
        except:
            elbow_angle = None

    if elbow_angle is not None:
        angle_history.append(elbow_angle)
        elbow_angle_sm = sum(angle_history)/len(angle_history)

        if state == 'up' and elbow_angle_sm <= DOWN_ANGLE:
            state = 'down'
            in_dip = True
            dip_start_time = t
            current_dip_min_angle = elbow_angle_sm

        elif state == 'down' and elbow_angle_sm >= UP_ANGLE:
            state = 'up'
            if in_dip:
                dip_duration = t - dip_start_time
                is_correct = current_dip_min_angle <= DOWN_ANGLE and dip_duration >= MIN_DIP_DURATION
                rep = {
                    'count': len(reps)+1,
                    'down_time': round(dip_start_time,3),
                    'up_time': round(t,3),
                    'dip_duration_sec': round(dip_duration,3),
                    'min_elbow_angle': round(current_dip_min_angle,2),
                    'correct': is_correct
                }
                reps.append(rep)
                in_dip = False
                dip_start_time = None
                current_dip_min_angle = 180

        if in_dip and elbow_angle_sm < current_dip_min_angle:
            current_dip_min_angle = elbow_angle_sm

    if elbow_angle is not None:
        cv2.putText(frame, f'Elbow: {int(elbow_angle_sm)}', (10,30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
    cv2.putText(frame, f'Pushups: {len(reps)}', (10,60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0,255,255),2)
    cv2.putText(frame, f'State: {state}', (10,95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,200,0),2)
    dip_time_display = t - dip_start_time if in_dip and dip_start_time else 0.0
    cv2.putText(frame, f'Dip: {dip_time_display:.3f}s', (10,130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0),2)
    correct_count = sum(1 for r in reps if r['correct'])
    bad_count = len(reps) - correct_count
    cv2.putText(frame, f'Correct: {correct_count}', (10,160),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
    cv2.putText(frame, f'Bad: {bad_count}', (10,190),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255),2)

    out_vid.write(frame)

cap.release()
out_vid.release()
pose.close()

csv_path = os.path.join(output_folder, f"{filename}_pushup_log.csv")
if reps:
    pd.DataFrame(reps).to_csv(csv_path, index=False)
    print(f"SUCCESS: {len(reps)} reps detected")
else:
    print("SUCCESS: No reps detected")
