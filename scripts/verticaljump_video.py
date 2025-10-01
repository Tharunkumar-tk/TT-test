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
PROC_W, PROC_H = 960, 540  # fixed resolution for display
PIXEL_TO_CM = 0.26
PIXEL_TO_M = PIXEL_TO_CM / 100
SMOOTH_N = 5  # frames to smooth hip y

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
csv_path = os.path.join(output_folder, f"{filename}_vertical_jump_log.csv")

# -------- Video Setup --------
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS) or 30
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
video_duration_sec = total_frames / fps
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_vid = cv2.VideoWriter(output_video_path, fourcc, fps, (PROC_W, PROC_H))

# -------- MediaPipe Setup --------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, model_complexity=1)
mp_draw = mp.solutions.drawing_utils

# -------- Jump Variables --------
baseline_y = None
in_air = False
peak_y = None
jump_count = 0
jump_data = []
hip_history = deque(maxlen=SMOOTH_N)
max_jump_height_px = 0
time_of_max_height = 0
air_start_time = 0
air_time = 0  # initialize air_time

frame_idx = 0

# -------- Processing Loop --------
while True:
    ret, frame = cap.read()
    if not ret: break
    frame_idx += 1
    t = frame_idx / fps

    # Resize for consistent display
    frame = cv2.resize(frame, (PROC_W, PROC_H))

    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        lm = results.pose_landmarks.landmark

        # Mid-hip
        left_hip = lm_xy(lm[mp_pose.PoseLandmark.LEFT_HIP], PROC_W, PROC_H)
        right_hip = lm_xy(lm[mp_pose.PoseLandmark.RIGHT_HIP], PROC_W, PROC_H)
        mid_hip_y = (left_hip[1] + right_hip[1]) / 2

        hip_history.append(mid_hip_y)
        hip_smoothed = np.mean(hip_history)

        if baseline_y is None:
            baseline_y = hip_smoothed

        # Jump detection
        if not in_air and hip_smoothed < baseline_y - 20:
            in_air = True
            peak_y = hip_smoothed
            air_start_time = t
            air_time = 0  # reset air_time at takeoff
        elif in_air:
            peak_y = min(peak_y, hip_smoothed)
            air_time = t - air_start_time  # update air_time continuously
            # Landing detected
            if hip_smoothed >= baseline_y - 5:
                in_air = False
                jump_height_px = baseline_y - peak_y
                jump_height_m = jump_height_px * PIXEL_TO_M
                jump_count += 1
                jump_data.append({
                    'count': jump_count,
                    'takeoff_time': round(air_start_time,3),
                    'landing_time': round(t,3),
                    'air_time_s': round(air_time,3),
                    'jump_height_px': round(jump_height_px,2),
                    'jump_height_m': round(jump_height_m,3)
                })
                if jump_height_px > max_jump_height_px:
                    max_jump_height_px = jump_height_px
                    time_of_max_height = air_start_time
                peak_y = None
                air_time = 0  # reset after landing

        # -------- Display --------
        cv2.putText(frame, f"Jump Count: {jump_count}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,255),2)
        cv2.putText(frame, f"Peak Height: {max_jump_height_px*PIXEL_TO_M:.2f} m", (10,70), cv2.FONT_HERSHEY_SIMPLEX,0.8,(0,255,0),2)
        cv2.putText(frame, f"Air Time: {air_time:.2f}s" if in_air else "", (10,110), cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,0,0),2)
        cv2.putText(frame, f"Video Time: {t:.2f}s", (10,150), cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,0),2)

    cv2.imshow("Vertical Jump Tracker", frame)
    out_vid.write(frame)
    if cv2.waitKey(int(1000/fps)) & 0xFF == 27:  # ESC
        break

# -------- Cleanup --------
cap.release()
out_vid.release()
cv2.destroyAllWindows()
pose.close()

# -------- Save CSV --------
if jump_data:
    pd.DataFrame(jump_data).to_csv(csv_path, index=False)
    print(f"Saved {csv_path} with {len(jump_data)} jumps")
else:
    print("No jumps detected.")

print(f"Total video duration: {video_duration_sec:.2f}s")
print(f"Maximum jump height: {max_jump_height_px*PIXEL_TO_M:.2f}m at {time_of_max_height:.2f}s")
