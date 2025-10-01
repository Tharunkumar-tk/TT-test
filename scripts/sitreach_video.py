import cv2
import os
import mediapipe as mp
from tkinter import Tk, filedialog
from collections import deque
import numpy as np
import pandas as pd

# -------- Utilities --------
def lm_xy(lm, w, h):
    return (lm.x*w, lm.y*h)

# -------- Settings --------
PROC_W, PROC_H = 960, 540
PIXEL_TO_CM = 0.26
PIXEL_TO_M = PIXEL_TO_CM / 100
SMOOTH_N = 5

# -------- File Selection --------
Tk().withdraw()
video_path = filedialog.askopenfilename(title="Select Video", filetypes=[("Video Files","*.mp4;*.avi;*.mov")])
if not video_path:
    print("No file selected, exiting...")
    exit()

filename = os.path.splitext(os.path.basename(video_path))[0]
output_folder = filename
os.makedirs(output_folder, exist_ok=True)
output_video_path = os.path.join(output_folder, f"{filename}_annotated.mp4")
csv_path = os.path.join(output_folder, f"{filename}_sit_and_reach_log.csv")

# -------- Video Setup --------
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_vid = cv2.VideoWriter(output_video_path, fourcc, fps, (PROC_W, PROC_H))

# -------- MediaPipe Setup --------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)
mp_draw = mp.solutions.drawing_utils

# -------- Variables --------
reach_history = deque(maxlen=SMOOTH_N)
max_reach_px = 0
time_of_max_reach = 0
reach_data = []

frame_idx = 0

# -------- Processing Loop --------
while True:
    ret, frame = cap.read()
    if not ret: break
    frame_idx += 1
    t = frame_idx / fps

    frame = cv2.resize(frame, (PROC_W, PROC_H))
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        lm = results.pose_landmarks.landmark

        try:
            # Feet (average)
            left_foot = lm_xy(lm[mp_pose.PoseLandmark.LEFT_FOOT_INDEX], PROC_W, PROC_H)
            right_foot = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX], PROC_W, PROC_H)
            foot_x = (left_foot[0] + right_foot[0]) / 2

            # Hands (average)
            left_hand = lm_xy(lm[mp_pose.PoseLandmark.LEFT_WRIST], PROC_W, PROC_H)
            right_hand = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_WRIST], PROC_W, PROC_H)
            hand_x = (left_hand[0] + right_hand[0]) / 2

            # Forward reach distance (positive if hands ahead of feet)
            reach_px = hand_x - foot_x
            reach_history.append(reach_px)
            reach_smoothed = np.mean(reach_history)

            # Update max reach
            if reach_smoothed > max_reach_px:
                max_reach_px = reach_smoothed
                time_of_max_reach = t

            # Log reach data
            reach_data.append({
                'time_s': round(t,3),
                'reach_px': round(reach_smoothed,2),
                'reach_m': round(reach_smoothed*PIXEL_TO_M,3)
            })

            # -------- Display --------
            cv2.putText(frame, f"Current Reach: {reach_smoothed*PIXEL_TO_M:.2f} m", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
            cv2.putText(frame, f"Max Reach: {max_reach_px*PIXEL_TO_M:.2f} m", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255),2)
            cv2.putText(frame, f"Time: {t:.2f}s", (10,110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,0),2)

        except:
            pass

    out_vid.write(frame)
    cv2.imshow("Sit and Reach Tracker", frame)
    if cv2.waitKey(int(1000/fps)) & 0xFF == 27:  # ESC
        break

# -------- Cleanup --------
cap.release()
out_vid.release()
cv2.destroyAllWindows()
pose.close()

# -------- Save CSV --------
if reach_data:
    pd.DataFrame(reach_data).to_csv(csv_path, index=False)
    print(f"Saved {csv_path}")
    print(f"Max Reach: {max_reach_px*PIXEL_TO_M:.2f} m at {time_of_max_reach:.2f} s")
else:
    print("No reach data detected.")
