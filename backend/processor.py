import os
import sys
import json
import subprocess
import pandas as pd
from pathlib import Path
import shutil

class WorkoutProcessor:
    def __init__(self):
        self.scripts_dir = Path(__file__).parent.parent / "scripts"
        self.temp_dir = Path(__file__).parent / "temp"
        self.temp_dir.mkdir(exist_ok=True)

        self.activity_script_map = {
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
            },
            "Sit-ups": {
                "video": "situp_video.py",
                "live": None
            },
            "Sit & Reach": {
                "video": "sitreach_video.py",
                "live": None
            },
            "Standing Broad Jump": {
                "video": "verticalbroadjump_video.py",
                "live": None
            }
        }

    def process_workout(self, activity_name, video_path, mode="video"):
        """
        Process workout video using the appropriate Python script.
        Returns a dictionary with results and paths to annotated video and CSV.
        """
        if activity_name not in self.activity_script_map:
            return {"error": f"Activity '{activity_name}' not supported"}

        script_name = self.activity_script_map[activity_name].get(mode)
        if not script_name:
            return {"error": f"Mode '{mode}' not supported for {activity_name}"}

        script_path = self.scripts_dir / script_name
        if not script_path.exists():
            return {"error": f"Script not found: {script_path}"}

        try:
            result = self._run_script(script_path, video_path, activity_name)
            return result
        except Exception as e:
            return {"error": str(e)}

    def _run_script(self, script_path, video_path, activity_name):
        """Run the Python script and collect outputs"""
        video_filename = Path(video_path).stem
        output_folder = Path(video_path).parent / video_filename

        process = subprocess.Popen(
            [sys.executable, str(script_path), str(video_path)],
            cwd=str(script_path.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = process.communicate(timeout=300)
        except subprocess.TimeoutExpired:
            process.kill()
            return {"error": "Processing timeout exceeded (5 minutes)"}

        if process.returncode != 0:
            return {"error": f"Script failed: {stderr or 'Unknown error'}"}

        annotated_video = self._find_annotated_video(output_folder)
        csv_file = self._find_csv_file(output_folder)

        results = {
            "status": "success",
            "annotated_video": str(annotated_video) if annotated_video else None,
            "csv_file": str(csv_file) if csv_file else None,
            "raw_output": stdout
        }

        if csv_file and csv_file.exists():
            results["metrics"] = self._parse_csv(csv_file, activity_name)

        return results

    def _find_annotated_video(self, folder):
        """Find the annotated video file"""
        if not folder.exists():
            return None
        for ext in ['.mp4', '.avi', '.mov']:
            for file in folder.glob(f'*_annotated{ext}'):
                return file
        return None

    def _find_csv_file(self, folder):
        """Find the CSV log file"""
        if not folder.exists():
            return None
        csv_files = list(folder.glob('*.csv'))
        return csv_files[0] if csv_files else None

    def _parse_csv(self, csv_path, activity_name):
        """Parse CSV and map to UI-friendly metrics"""
        try:
            df = pd.read_csv(csv_path)

            if activity_name in ["Push-ups", "Pull-ups", "Sit-ups"]:
                return self._parse_rep_based(df, activity_name)
            elif activity_name == "Vertical Jump":
                return self._parse_vertical_jump(df)
            elif activity_name == "Shuttle Run":
                return self._parse_shuttle_run(df)
            elif activity_name == "Sit & Reach":
                return self._parse_sit_reach(df)
            elif activity_name == "Standing Broad Jump":
                return self._parse_broad_jump(df)
            else:
                return {"raw_data": df.to_dict('records')}

        except Exception as e:
            return {"error": f"Failed to parse CSV: {str(e)}"}

    def _parse_rep_based(self, df, activity_name):
        """Parse pushups, pullups, situps"""
        total_reps = len(df)
        correct_reps = df['correct'].sum() if 'correct' in df.columns else total_reps
        incorrect_reps = total_reps - correct_reps

        avg_duration = df['dip_duration_sec'].mean() if 'dip_duration_sec' in df.columns else 0

        total_time = 0
        if 'up_time' in df.columns and len(df) > 0:
            total_time = df['up_time'].max()
        elif 'down_time' in df.columns and len(df) > 0:
            total_time = df['down_time'].max()

        min_angle = df['min_elbow_angle'].min() if 'min_elbow_angle' in df.columns else 0
        max_angle = df['min_elbow_angle'].max() if 'min_elbow_angle' in df.columns else 0

        return {
            "reps_completed": total_reps,
            "correct_reps": int(correct_reps),
            "incorrect_reps": incorrect_reps,
            "time_sec": round(total_time, 2),
            "avg_rep_duration_sec": round(avg_duration, 2),
            "min_angle": round(min_angle, 2),
            "max_angle": round(max_angle, 2),
            "form_accuracy_percent": round((correct_reps / total_reps * 100) if total_reps > 0 else 0, 1)
        }

    def _parse_vertical_jump(self, df):
        """Parse vertical jump data"""
        if len(df) == 0:
            return {"error": "No jumps detected"}

        max_height = df['jump_height_m'].max()
        avg_height = df['jump_height_m'].mean()
        total_jumps = len(df)
        max_air_time = df['air_time_s'].max() if 'air_time_s' in df.columns else 0

        max_idx = df['jump_height_m'].idxmax()
        time_of_max = df.loc[max_idx, 'takeoff_time'] if 'takeoff_time' in df.columns else 0

        total_time = df['landing_time'].max() if 'landing_time' in df.columns else 0

        return {
            "jump_height_m": round(max_height, 3),
            "avg_jump_height_m": round(avg_height, 3),
            "air_time_s": round(max_air_time, 2),
            "total_jumps": total_jumps,
            "time_of_max_height_sec": round(time_of_max, 2),
            "total_time_sec": round(total_time, 2)
        }

    def _parse_shuttle_run(self, df):
        """Parse shuttle run data"""
        if len(df) == 0:
            return {"error": "No shuttle runs detected"}

        total_time = df['split_time'].sum() if 'split_time' in df.columns else 0
        laps = len(df)
        avg_split = df['split_time'].mean() if 'split_time' in df.columns else 0

        distance = laps * 20

        return {
            "distance_m": distance,
            "time_sec": round(total_time, 2),
            "laps_completed": laps,
            "avg_split_time_sec": round(avg_split, 2)
        }

    def _parse_sit_reach(self, df):
        """Parse sit and reach data"""
        if len(df) == 0:
            return {"error": "No measurements detected"}

        best_reach = df['reach_cm'].max() if 'reach_cm' in df.columns else 0
        total_time = df['time_sec'].sum() if 'time_sec' in df.columns else 0

        return {
            "reach_cm": round(best_reach, 2),
            "time_sec": round(total_time, 2)
        }

    def _parse_broad_jump(self, df):
        """Parse standing broad jump data"""
        if len(df) == 0:
            return {"error": "No jumps detected"}

        max_distance = df['distance_m'].max() if 'distance_m' in df.columns else 0
        avg_distance = df['distance_m'].mean() if 'distance_m' in df.columns else 0
        total_jumps = len(df)

        return {
            "max_distance_m": round(max_distance, 2),
            "avg_distance_m": round(avg_distance, 2),
            "total_jumps": total_jumps
        }


def main():
    """CLI interface for testing"""
    if len(sys.argv) < 3:
        print("Usage: python processor.py <activity_name> <video_path> [mode]")
        sys.exit(1)

    activity = sys.argv[1]
    video_path = sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "video"

    processor = WorkoutProcessor()
    result = processor.process_workout(activity, video_path, mode)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
