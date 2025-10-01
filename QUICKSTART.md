# Quick Start Guide

Get FitVision running in 5 minutes!

## Installation (One Time)

### Step 1: Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ..
```

## Running the App (Every Time)

### Open 2 Terminals

**Terminal 1 - Backend:**
```bash
cd backend
./start.sh  # Windows: start.bat
```
✅ Wait for "Uvicorn running on http://0.0.0.0:8000"

**Terminal 2 - Frontend:**
```bash
npm run dev
```
✅ Open browser to http://localhost:5173

## Test It Out

1. **Click any activity** (e.g., "Push-ups")
2. **Upload a video** or record one
3. **Wait 15-30 seconds** for processing
4. **View your results** with annotated video!

## File Structure

```
your-video.mp4                    # Input
    ↓
backend/uploads/{session-id}/
    ├── input.mp4                 # Saved upload
    └── input/
        ├── input_annotated.mp4   # Annotated video
        └── input_pushup_log.csv  # Metrics CSV
```

## Troubleshooting

**"Backend Offline" warning?**
→ Start the backend server in Terminal 1

**"Module not found" error?**
→ Run `pip install -r backend/requirements.txt`

**"Port already in use"?**
→ Backend: Kill process on port 8000
→ Frontend: Vite will auto-select next port

**Processing fails?**
→ Check video shows full body
→ Ensure good lighting
→ Try a different video

## What Each Component Does

| Component | Purpose | Location |
|-----------|---------|----------|
| Frontend | User interface | React app (port 5173) |
| Backend | API server | FastAPI (port 8000) |
| Scripts | Pose detection | Python + MediaPipe |

## Supported Formats

- **Video**: MP4, AVI, MOV
- **Duration**: Up to 5 minutes
- **Size**: Up to 100MB
- **Resolution**: Any (will be resized)

## Output

### Annotated Video
- Pose skeleton overlay
- Rep counter
- Form indicators
- Time stamps

### CSV Log
- Per-rep metrics
- Timestamps
- Angles/measurements
- Form flags

### UI Metrics
- Total reps
- Correct/incorrect
- Time taken
- Form accuracy %

## Next Steps

- ✅ System running
- ✅ Test video processed
- 📖 Read [SETUP.md](./SETUP.md) for details
- 📖 Read [INTEGRATION.md](./INTEGRATION.md) for architecture
- 🏋️ Start tracking your workouts!

## Common Activities

### Push-ups
- Shows full body, front or side view
- Clear view of elbows and shoulders
- 30-60 second clips work best

### Pull-ups
- Shows full body from front
- Bar visible at top
- Clear arm and shoulder landmarks

### Vertical Jump
- Side view preferred
- Full body in frame before/during/after
- Stationary camera

### Shuttle Run
- Wide angle showing full court/track
- Side view if possible
- Track all turns and sprints

## Performance

- **10s video**: ~5s processing
- **30s video**: ~15s processing
- **60s video**: ~30s processing

Processing time = ~0.5x video length

## Privacy

✅ All processing happens locally
✅ No data sent to cloud
✅ Your videos stay on your device
✅ No internet required (after install)

---

**Ready to go!** 🚀 Open http://localhost:5173 and start your first workout analysis!
