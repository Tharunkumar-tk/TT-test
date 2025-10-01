# FitVision Backend - Offline Workout Processing

This backend service processes workout videos locally using Python and MediaPipe for pose detection. All processing happens on your device - no cloud dependencies.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Webcam (for live mode)

## Quick Start

### Linux/Mac

```bash
cd backend
chmod +x start.sh
./start.sh
```

### Windows

```cmd
cd backend
start.bat
```

### Manual Start

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

The server will start on `http://localhost:8000`

## Supported Activities

- **Push-ups** (video + live)
- **Pull-ups** (video + live)
- **Vertical Jump** (video + live)
- **Shuttle Run** (video + live)
- **Sit-ups** (video only)
- **Sit & Reach** (video only)
- **Standing Broad Jump** (video only)

## API Endpoints

### POST /api/process-workout
Process a workout video and get analysis results.

**Request:**
- `video`: File (video file)
- `activity`: String (activity name)
- `mode`: String ('video' or 'live')

**Response:**
```json
{
  "session_id": "uuid",
  "status": "success",
  "metrics": {
    "reps_completed": 20,
    "correct_reps": 18,
    "time_sec": 45.2,
    "form_accuracy_percent": 90.0
  },
  "annotated_video_url": "/api/video/{session_id}/annotated",
  "csv_url": "/api/csv/{session_id}"
}
```

### GET /api/video/{session_id}/annotated
Download the annotated video with pose overlay and rep counts.

### GET /api/csv/{session_id}
Download the detailed CSV log file with frame-by-frame metrics.

### GET /api/health
Health check endpoint.

## How It Works

1. **Video Upload**: User uploads or records a workout video through the UI
2. **Processing**: Backend runs the appropriate Python script with MediaPipe
3. **Analysis**: Pose landmarks are detected and analyzed for reps, form, and metrics
4. **Output**: Annotated video + CSV log file are generated
5. **Results**: Metrics are parsed and displayed in the UI

## Output Files

For each processing session, the following files are generated:

- `{filename}_annotated.mp4` - Video with pose skeleton and rep counter overlay
- `{filename}_log.csv` - Detailed metrics for each rep/jump/lap

## CSV Format

### Push-ups/Pull-ups/Sit-ups
```csv
count,down_time,up_time,dip_duration_sec,min_elbow_angle,correct
1,2.5,3.2,0.7,65,true
```

### Vertical Jump
```csv
count,takeoff_time,landing_time,air_time_s,jump_height_px,jump_height_m
1,5.2,5.8,0.6,120,0.31
```

### Shuttle Run
```csv
lap,split_time,total_time
1,5.2,5.2
```

## Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed: `python3 --version`
- Check if port 8000 is available
- Try manually installing: `pip install -r requirements.txt`

### Video processing fails
- Ensure good lighting and clear view of full body
- Check that the activity is supported
- Verify video format (MP4, AVI, MOV)

### No pose detected
- Ensure subject is fully visible in frame
- Improve lighting conditions
- Try recording at a different angle

## Development

To modify the processing logic:
1. Edit the Python scripts in `/scripts` directory
2. Update `processor.py` to handle new metrics
3. Update `workoutService.ts` in frontend for UI mapping

## Privacy

All video processing happens locally on your device. No data is sent to external servers.
