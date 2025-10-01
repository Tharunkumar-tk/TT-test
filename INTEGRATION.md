# Integration Guide: UI ↔ Backend ↔ Python Scripts

Complete guide to how the FitVision components work together.

## System Overview

```
┌──────────────────────────────────────────────────────────────────┐
│                         User Interface                            │
│  React Components (TypeScript)                                    │
│  - WorkoutUploadScreen.tsx: Video selection                       │
│  - VideoProcessor.tsx: Processing & results                       │
│  - ActivityDetail.tsx: Activity info                              │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ HTTP POST /api/process-workout
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                      Backend API Server                           │
│  FastAPI (Python)                                                 │
│  - server.py: HTTP endpoints                                      │
│  - processor.py: Script execution & data parsing                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             │ subprocess.Popen()
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    Python Analysis Scripts                        │
│  MediaPipe + OpenCV                                               │
│  - run_pushup_video.py: Push-up detection                        │
│  - pullup_video.py: Pull-up detection                            │
│  - verticaljump_video.py: Jump measurement                        │
│  Output: Annotated MP4 + CSV metrics                             │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Video Upload (Frontend)

**File:** `src/components/workout/WorkoutUploadScreen.tsx`

```typescript
// User selects or records video
const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
  const file = event.target.files?.[0];
  if (file && file.type.startsWith('video/')) {
    onVideoSelected(file); // Triggers processing
  }
};
```

### 2. API Call (Service Layer)

**File:** `src/services/workoutService.ts`

```typescript
export async function processWorkout(
  videoFile: File,
  activityName: string,
  mode: 'video' | 'live' = 'video'
): Promise<WorkoutResult> {
  const formData = new FormData();
  formData.append('video', videoFile);
  formData.append('activity', activityName);
  formData.append('mode', mode);

  const response = await fetch(`${BACKEND_URL}/api/process-workout`, {
    method: 'POST',
    body: formData,
  });

  return await response.json();
}
```

### 3. Backend Processing (FastAPI)

**File:** `backend/server.py`

```python
@app.post("/api/process-workout")
async def process_workout(
    video: UploadFile = File(...),
    activity: str = Form(...),
    mode: str = Form("video")
):
    # Save uploaded video
    session_id = str(uuid.uuid4())
    video_path = UPLOAD_DIR / session_id / f"input{video_ext}"

    # Process with Python script
    result = processor.process_workout(activity, str(video_path), mode)

    # Return results with URLs
    return {
        "session_id": session_id,
        "metrics": result["metrics"],
        "annotated_video_url": f"/api/video/{session_id}/annotated",
        "csv_url": f"/api/csv/{session_id}"
    }
```

### 4. Script Execution (Processor)

**File:** `backend/processor.py`

```python
def _run_script(self, script_path, video_path, activity_name):
    # Execute Python script with video path
    process = subprocess.Popen(
        [sys.executable, str(script_path), str(video_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    stdout, stderr = process.communicate(timeout=300)

    # Find output files
    annotated_video = self._find_annotated_video(output_folder)
    csv_file = self._find_csv_file(output_folder)

    # Parse CSV to metrics
    metrics = self._parse_csv(csv_file, activity_name)

    return {
        "status": "success",
        "annotated_video": str(annotated_video),
        "csv_file": str(csv_file),
        "metrics": metrics
    }
```

### 5. Python Script Processing

**File:** `scripts/run_pushup_video.py`

```python
# Accept video path from command line
video_path = sys.argv[1]

# Setup video capture
cap = cv2.VideoCapture(video_path)

# Initialize MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5)

# Process each frame
while True:
    ret, frame = cap.read()
    if not ret: break

    # Detect pose
    results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Calculate angles and count reps
    if results.pose_landmarks:
        elbow_angle = calculate_elbow_angle(results.pose_landmarks)
        if elbow_angle < DOWN_ANGLE:
            state = 'down'
        elif elbow_angle > UP_ANGLE and state == 'down':
            reps.append({'count': len(reps)+1, ...})
            state = 'up'

    # Draw annotations
    mp_draw.draw_landmarks(frame, results.pose_landmarks)
    out_vid.write(frame)

# Save outputs
pd.DataFrame(reps).to_csv(csv_path)
```

### 6. Results Display (Frontend)

**File:** `src/components/workout/VideoProcessor.tsx`

```typescript
const processVideo = async (file: File) => {
  // Call backend API
  const workoutResult = await processWorkout(file, activityName, 'video');

  // Format metrics for UI
  const formattedMetrics = formatMetricsForDisplay(
    workoutResult.metrics,
    activityName
  );

  // Display results
  setResult({
    type: 'good',
    videoUrl: workoutResult.annotated_video_url,
    metrics: workoutResult.metrics,
    formattedMetrics
  });
};
```

## CSV → UI Mapping

### Push-ups / Pull-ups / Sit-ups

**CSV Format:**
```csv
count,down_time,up_time,dip_duration_sec,min_elbow_angle,correct
1,2.5,3.2,0.7,65,true
2,4.1,4.9,0.8,62,true
```

**Parsed Metrics:**
```json
{
  "reps_completed": 20,
  "correct_reps": 18,
  "incorrect_reps": 2,
  "time_sec": 45.2,
  "form_accuracy_percent": 90.0,
  "avg_rep_duration_sec": 0.75
}
```

**UI Display:**
```
┌─────────────────────┐
│  Reps Completed: 20 │
│  Correct Reps: 18   │
│  Incorrect: 2       │
│  Time: 45.2s        │
│  Form Accuracy: 90% │
│  Avg Duration: 0.75s│
└─────────────────────┘
```

### Vertical Jump

**CSV Format:**
```csv
count,takeoff_time,landing_time,air_time_s,jump_height_m
1,5.2,5.8,0.6,0.31
2,8.5,9.2,0.7,0.35
```

**Parsed Metrics:**
```json
{
  "jump_height_m": 0.35,
  "avg_jump_height_m": 0.33,
  "air_time_s": 0.7,
  "total_jumps": 2
}
```

**UI Display:**
```
┌──────────────────────────┐
│  Jump Height: 0.35m      │
│  Avg Height: 0.33m       │
│  Air Time: 0.7s          │
│  Total Jumps: 2          │
└──────────────────────────┘
```

### Shuttle Run

**CSV Format:**
```csv
lap,split_time,total_time
1,5.2,5.2
2,5.5,10.7
```

**Parsed Metrics:**
```json
{
  "distance_m": 40,
  "time_sec": 10.7,
  "laps_completed": 2,
  "avg_split_time_sec": 5.35
}
```

**UI Display:**
```
┌───────────────────────────┐
│  Distance: 40m            │
│  Time: 10.7s              │
│  Laps: 2                  │
│  Avg Split: 5.35s         │
└───────────────────────────┘
```

## File Locations

### Input
```
backend/uploads/
└── {session-id}/
    └── input.mp4    # Uploaded video
```

### Output
```
backend/uploads/
└── {session-id}/
    └── input/       # Output folder (named after input file)
        ├── input_annotated.mp4      # Annotated video
        └── input_pushup_log.csv     # Metrics log
```

## Activity → Script Mapping

Defined in `backend/processor.py`:

```python
activity_script_map = {
    "Push-ups": {
        "video": "run_pushup_video.py",
        "live": "pushup_live.py"
    },
    "Pull-ups": {
        "video": "pullup_video.py",
        "live": "pullup_live.py"
    },
    "Vertical Jump": {
        "video": "verticaljump_video.py",
        "live": "verticaljump_live.py"
    },
    "Shuttle Run": {
        "video": "shuttlerun_video.py",
        "live": "shuttlerun_live.py"
    }
}
```

## Error Handling

### Frontend
```typescript
try {
  const result = await processWorkout(file, activityName);
  setResult(result);
} catch (error) {
  toast.error(error.message);
  onRetry();
}
```

### Backend
```python
try:
    result = processor.process_workout(activity, video_path)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
```

### Script
```python
if not video_path or not os.path.exists(video_path):
    print(f"Error: Video file not found: {video_path}")
    sys.exit(1)
```

## Adding New Activities

### 1. Create Python Script
```python
# scripts/new_activity_video.py
import cv2, mediapipe, pandas
# ... processing logic
# Output: annotated video + CSV
```

### 2. Update Processor Mapping
```python
# backend/processor.py
"New Activity": {
    "video": "new_activity_video.py",
    "live": None
}
```

### 3. Add CSV Parser
```python
# backend/processor.py
def _parse_new_activity(self, df):
    return {
        "metric1": df['column1'].max(),
        "metric2": df['column2'].mean()
    }
```

### 4. Update Service Formatter
```typescript
// src/services/workoutService.ts
if (activityName === 'New Activity') {
  formatted.push({
    label: 'Metric 1',
    value: metrics.metric1
  });
}
```

### 5. Add to Activity List
```typescript
// src/components/activities/ActivityDetail.tsx
'New Activity': {
  description: '...',
  muscles: ['...'],
  category: '...'
}
```

## Testing Integration

### 1. Backend Health Check
```bash
curl http://localhost:8000/api/health
# Expected: {"status":"healthy"}
```

### 2. Test Script Directly
```bash
python scripts/run_pushup_video.py path/to/video.mp4
# Check for: annotated.mp4 + CSV in output folder
```

### 3. Test API Endpoint
```bash
curl -X POST http://localhost:8000/api/process-workout \
  -F "video=@test.mp4" \
  -F "activity=Push-ups" \
  -F "mode=video"
```

### 4. Test Frontend
1. Start backend: `cd backend && ./start.sh`
2. Start frontend: `npm run dev`
3. Upload video through UI
4. Verify results display

## Performance Optimization

- **Video Resolution**: Scripts resize to 960x540 for faster processing
- **Frame Processing**: Every frame analyzed at 30 FPS
- **Parallel Processing**: Backend can handle multiple requests
- **Caching**: Videos stored in session folders for quick retrieval

## Security Considerations

- **File Upload Limits**: Max 100MB video files
- **Session Isolation**: Each upload gets unique session ID
- **Auto-Cleanup**: Consider adding cleanup for old session folders
- **CORS**: Currently allows all origins (adjust for production)

## Debugging Tips

1. **Check Backend Logs**: Look at terminal running `start.sh`
2. **Inspect Network Tab**: View API request/response in browser
3. **Run Script Manually**: Test scripts independently
4. **Check File Permissions**: Ensure output folders are writable
5. **Verify Python Packages**: `pip list | grep mediapipe`

---

All components work together to provide a seamless, offline workout analysis experience!
