from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid
from processor import WorkoutProcessor
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = WorkoutProcessor()
UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.post("/api/process-workout")
async def process_workout(
    video: UploadFile = File(...),
    activity: str = Form(...),
    mode: str = Form("video")
):
    """
    Process a workout video
    """
    session_id = str(uuid.uuid4())
    session_dir = UPLOAD_DIR / session_id
    session_dir.mkdir(exist_ok=True)

    video_ext = Path(video.filename).suffix
    video_path = session_dir / f"input{video_ext}"

    try:
        with video_path.open("wb") as buffer:
            shutil.copyfileobj(video.file, buffer)

        result = processor.process_workout(activity, str(video_path), mode)

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        response = {
            "session_id": session_id,
            "status": result["status"],
            "metrics": result.get("metrics", {}),
            "annotated_video_url": f"/api/video/{session_id}/annotated",
            "csv_url": f"/api/csv/{session_id}"
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/video/{session_id}/annotated")
async def get_annotated_video(session_id: str):
    """
    Retrieve the annotated video
    """
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")

    input_filename = None
    for file in session_dir.glob("input.*"):
        input_filename = file.stem
        break

    if not input_filename:
        raise HTTPException(status_code=404, detail="Input file not found")

    output_dir = session_dir / input_filename
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Output not found")

    for ext in ['.mp4', '.avi', '.mov']:
        for video_file in output_dir.glob(f'*_annotated{ext}'):
            return FileResponse(
                video_file,
                media_type=f"video/{ext[1:]}",
                filename=f"annotated{ext}"
            )

    raise HTTPException(status_code=404, detail="Annotated video not found")


@app.get("/api/csv/{session_id}")
async def get_csv(session_id: str):
    """
    Retrieve the CSV log file
    """
    session_dir = UPLOAD_DIR / session_id
    if not session_dir.exists():
        raise HTTPException(status_code=404, detail="Session not found")

    input_filename = None
    for file in session_dir.glob("input.*"):
        input_filename = file.stem
        break

    if not input_filename:
        raise HTTPException(status_code=404, detail="Input file not found")

    output_dir = session_dir / input_filename
    if not output_dir.exists():
        raise HTTPException(status_code=404, detail="Output not found")

    csv_files = list(output_dir.glob('*.csv'))
    if csv_files:
        return FileResponse(
            csv_files[0],
            media_type="text/csv",
            filename="workout_log.csv"
        )

    raise HTTPException(status_code=404, detail="CSV file not found")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
