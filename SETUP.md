# FitVision Setup Guide

Complete guide for setting up the offline workout analysis system.

## System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16.x or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB free space
- **Webcam**: Required for live recording mode
- **OS**: Windows 10+, macOS 10.15+, or Linux

## Installation

### Step 1: Install Python Dependencies

#### Linux/Mac

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Windows

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Install Node.js Dependencies

```bash
npm install
```

## Running the Application

You need to run **both** the backend and frontend servers.

### Terminal 1: Start Backend Server

#### Linux/Mac
```bash
cd backend
chmod +x start.sh
./start.sh
```

#### Windows
```cmd
cd backend
start.bat
```

The backend will start on `http://localhost:8000`

### Terminal 2: Start Frontend Dev Server

```bash
npm run dev
```

The frontend will start on `http://localhost:5173` (or next available port)

## Verify Installation

1. **Check Backend Health**
   ```bash
   curl http://localhost:8000/api/health
   ```
   Should return: `{"status":"healthy"}`

2. **Open Frontend**
   - Navigate to `http://localhost:5173` in your browser
   - You should see the FitVision home screen

## Testing the System

1. **Select an Activity**
   - Choose "Push-ups" from the activity list
   - Click "Proceed to Workout"

2. **Upload a Test Video**
   - Click "Upload Video"
   - Select any video showing push-ups
   - Wait for processing (30-60 seconds for 30-second video)

3. **View Results**
   - Annotated video with pose overlay
   - Metrics: reps, form accuracy, timing
   - CSV download option

## Supported Activities

| Activity | Video Mode | Live Mode | Status |
|----------|-----------|-----------|---------|
| Push-ups | ✅ | ✅ | Fully Supported |
| Pull-ups | ✅ | ✅ | Fully Supported |
| Vertical Jump | ✅ | ✅ | Fully Supported |
| Shuttle Run | ✅ | ✅ | Fully Supported |
| Sit-ups | ✅ | ❌ | Video Only |
| Sit & Reach | ✅ | ❌ | Video Only |
| Standing Broad Jump | ✅ | ❌ | Video Only |

## Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 5173)
│  - Activity UI  │
│  - Video Upload │
│  - Results View │
└────────┬────────┘
         │ HTTP API
         ↓
┌─────────────────┐
│  FastAPI Server │ (Port 8000)
│  - Video Upload │
│  - Script Exec  │
│  - File Serving │
└────────┬────────┘
         │ subprocess
         ↓
┌─────────────────┐
│ Python Scripts  │
│  - MediaPipe    │
│  - OpenCV       │
│  - Pose Detect  │
└─────────────────┘
```

## Data Flow

1. **User uploads video** → Frontend (React)
2. **POST to /api/process-workout** → Backend (FastAPI)
3. **Save to temp folder** → File System
4. **Execute Python script** → Subprocess
5. **MediaPipe processes frames** → Pose Detection
6. **Generate annotated video + CSV** → Output Files
7. **Parse CSV metrics** → JSON Response
8. **Display results** → Frontend

## File Structure

```
project/
├── backend/
│   ├── server.py           # FastAPI server
│   ├── processor.py        # Workout processing logic
│   ├── requirements.txt    # Python dependencies
│   ├── start.sh           # Linux/Mac startup
│   ├── start.bat          # Windows startup
│   └── uploads/           # Temp video storage
├── scripts/
│   ├── run_pushup_video.py      # Push-up analysis
│   ├── pullup_video.py          # Pull-up analysis
│   ├── verticaljump_video.py    # Vertical jump analysis
│   └── ...                      # Other activity scripts
├── src/
│   ├── components/
│   │   └── workout/
│   │       ├── WorkoutInterface.tsx
│   │       ├── VideoProcessor.tsx
│   │       └── WorkoutUploadScreen.tsx
│   └── services/
│       └── workoutService.ts    # API client
└── package.json
```

## Troubleshooting

### Backend Issues

**Error: Python not found**
```bash
# Install Python 3.8+
# Linux: sudo apt install python3
# Mac: brew install python3
# Windows: Download from python.org
```

**Error: Module not found**
```bash
pip install -r backend/requirements.txt
```

**Error: Port 8000 already in use**
```bash
# Find and kill process
# Linux/Mac: lsof -ti:8000 | xargs kill -9
# Windows: netstat -ano | findstr :8000
```

### Frontend Issues

**Error: Cannot connect to backend**
- Ensure backend is running on port 8000
- Check `.env` file has `VITE_BACKEND_URL=http://localhost:8000`
- Restart frontend dev server

**Video upload fails**
- Check video format (MP4, AVI, MOV supported)
- Ensure video file size < 100MB
- Check backend logs for errors

### Processing Issues

**No pose detected**
- Ensure good lighting
- Keep full body in frame
- Try different camera angle
- Check video quality

**Reps not counting**
- Verify proper form
- Check if angle thresholds need adjustment
- Review annotated video for pose landmarks

**Processing takes too long**
- Reduce video resolution
- Shorten video duration
- Close other applications

## Performance Tips

1. **Video Quality**
   - 720p recommended (1080p may be slower)
   - 30 FPS ideal
   - Well-lit environment

2. **Processing Speed**
   - 10-second video: ~5 seconds
   - 30-second video: ~15 seconds
   - 60-second video: ~30 seconds

3. **System Resources**
   - Close unnecessary applications
   - GPU acceleration helps (if available)
   - 8GB RAM recommended for smooth processing

## Privacy & Security

- **All processing is local** - No cloud uploads
- **No external API calls** - Fully offline
- **Temporary files** - Auto-deleted after session
- **No data collection** - Your data stays on your device

## Development Mode

To modify the processing logic:

1. Edit Python scripts in `/scripts`
2. Update `processor.py` for new metrics
3. Update `workoutService.ts` for UI mapping
4. Test with sample videos
5. Restart backend server

## Production Deployment

For production use:

1. Build frontend: `npm run build`
2. Serve with nginx or similar
3. Run backend with gunicorn: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker backend.server:app`
4. Configure CORS properly
5. Add authentication if needed

## Support

For issues or questions:
1. Check this guide
2. Review backend logs
3. Test with sample videos
4. Verify dependencies installed

## Next Steps

1. ✅ System installed and running
2. ✅ Test with sample video
3. ✅ Review metrics and results
4. 📈 Start tracking your workouts!
