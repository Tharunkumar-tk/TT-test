import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from tkinter import Tk, filedialog
import pandas as pd
import os

# -------- Settings --------
PIXEL_TO_M = 0.01
SMOOTH_N = 5
DIR_FRAMES = 3
THRESHOLD_PIX = 5

# Resize target for full view (adjust as needed)
PROC_W, PROC_H = 960, 540

# -------- File Selection --------
Tk().withdraw()
video_path = filedialog.askopenfilename(
    title="Select Video", 
    filetypes=[("Video Files","*.mp4;*.avi;*.mov")]
)
if not video_path:
    print("No file selected, exiting...")
    exit()

filename = os.path.splitext(os.path.basename(video_path))[0]
output_folder = filename
os.makedirs(output_folder, exist_ok=True)
output_video_path = os.path.join(output_folder, f"{filename}_annotated.mp4")
csv_path = os.path.join(output_folder, f"{filename}_shuttle_run_positions.csv")

# -------- Video Setup --------
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_vid = cv2.VideoWriter(output_video_path, fourcc, fps, (PROC_W, PROC_H))

# -------- MediaPipe --------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)
mp_draw = mp.solutions.drawing_utils

# -------- Shuttle Run Variables --------
x_history = deque(maxlen=SMOOTH_N)
dir_history = deque(maxlen=DIR_FRAMES)
positions = []
run_count = 0
status = "Waiting"
direction = None
start_x = None
last_x = None
frame_idx = 0

# -------- Processing Loop --------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ✅ Resize to fixed resolution for consistent full view
    frame = cv2.resize(frame, (PROC_W, PROC_H))

    frame_idx += 1
    t = frame_idx / fps

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        lm = results.pose_landmarks.landmark

        keypoints_x = [
            lm[mp_pose.PoseLandmark.LEFT_ANKLE].x * PROC_W,
            lm[mp_pose.PoseLandmark.RIGHT_ANKLE].x * PROC_W,
            lm[mp_pose.PoseLandmark.LEFT_FOOT_INDEX].x * PROC_W,
            lm[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].x * PROC_W
        ]
        current_x = np.mean(keypoints_x)
        x_history.append(current_x)
        smoothed_x = np.mean(x_history)

        # Direction calculation
        if last_x is not None:
            delta = smoothed_x - last_x
            if delta > THRESHOLD_PIX:
                dir_history.append("forward")
            elif delta < -THRESHOLD_PIX:
                dir_history.append("backward")
        last_x = smoothed_x

        if len(dir_history) == DIR_FRAMES and all(d == dir_history[0] for d in dir_history):
            confirmed_dir = dir_history[0]
            if start_x is None:
                start_x = smoothed_x
                direction = confirmed_dir
                status = "Running Towards" if direction=="forward" else "Returning"
            elif direction != confirmed_dir:
                direction = confirmed_dir
                if confirmed_dir == "backward":
                    run_count += 1
                    status = "Returning"
                else:
                    status = "Running Towards"

        positions.append(smoothed_x)

    # -------- Display --------
    cv2.putText(frame, f"Run Count: {run_count}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255),2)
    cv2.putText(frame, f"Status: {status}", (10,70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0),2)
    if start_x is not None:
        distance_m = abs(smoothed_x - start_x) * PIXEL_TO_M
        cv2.putText(frame, f"Distance: {distance_m:.2f} m", (10,110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0),2)
    cv2.putText(frame, f"Time: {t:.2f} s", (10,150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200,200,0),2)

    cv2.imshow("Shuttle Run Counter", frame)
    out_vid.write(frame)

    if cv2.waitKey(int(1000/fps)) & 0xFF in [27, ord('q')]:
        break

# -------- Cleanup --------
cap.release()
out_vid.release()
cv2.destroyAllWindows()
pose.close()

# -------- Save CSV --------
if positions:
    pd.DataFrame({"frame": list(range(1,len(positions)+1)), "x_pos_px": positions}).to_csv(csv_path, index=False)
    print(f"Saved {csv_path} with {len(positions)} frames")
print(f"Total runs counted: {run_count}")
