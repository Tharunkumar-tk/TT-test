const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export interface WorkoutMetrics {
  reps_completed?: number;
  correct_reps?: number;
  incorrect_reps?: number;
  time_sec?: number;
  avg_rep_duration_sec?: number;
  form_accuracy_percent?: number;
  jump_height_m?: number;
  avg_jump_height_m?: number;
  air_time_s?: number;
  total_jumps?: number;
  distance_m?: number;
  laps_completed?: number;
  avg_split_time_sec?: number;
  reach_cm?: number;
  max_distance_m?: number;
  [key: string]: any;
}

export interface WorkoutResult {
  session_id: string;
  status: string;
  metrics: WorkoutMetrics;
  annotated_video_url: string;
  csv_url: string;
}

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

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to process workout');
  }

  const result = await response.json();
  return {
    ...result,
    annotated_video_url: `${BACKEND_URL}${result.annotated_video_url}`,
    csv_url: `${BACKEND_URL}${result.csv_url}`,
  };
}

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${BACKEND_URL}/api/health`, {
      method: 'GET',
    });
    return response.ok;
  } catch {
    return false;
  }
}

export function formatMetricsForDisplay(
  metrics: WorkoutMetrics,
  activityName: string
): Array<{ label: string; value: string | number }> {
  const formatted: Array<{ label: string; value: string | number }> = [];

  if (activityName === 'Push-ups' || activityName === 'Pull-ups' || activityName === 'Sit-ups') {
    if (metrics.reps_completed !== undefined) {
      formatted.push({ label: 'Reps Completed', value: metrics.reps_completed });
    }
    if (metrics.correct_reps !== undefined) {
      formatted.push({ label: 'Correct Reps', value: metrics.correct_reps });
    }
    if (metrics.incorrect_reps !== undefined) {
      formatted.push({ label: 'Incorrect Reps', value: metrics.incorrect_reps });
    }
    if (metrics.time_sec !== undefined) {
      formatted.push({ label: 'Time (s)', value: metrics.time_sec });
    }
    if (metrics.form_accuracy_percent !== undefined) {
      formatted.push({ label: 'Form Accuracy', value: `${metrics.form_accuracy_percent}%` });
    }
    if (metrics.avg_rep_duration_sec !== undefined) {
      formatted.push({ label: 'Avg Rep Duration (s)', value: metrics.avg_rep_duration_sec });
    }
  }

  if (activityName === 'Vertical Jump') {
    if (metrics.jump_height_m !== undefined) {
      formatted.push({ label: 'Jump Height (m)', value: metrics.jump_height_m });
    }
    if (metrics.avg_jump_height_m !== undefined) {
      formatted.push({ label: 'Avg Jump Height (m)', value: metrics.avg_jump_height_m });
    }
    if (metrics.air_time_s !== undefined) {
      formatted.push({ label: 'Air Time (s)', value: metrics.air_time_s });
    }
    if (metrics.total_jumps !== undefined) {
      formatted.push({ label: 'Total Jumps', value: metrics.total_jumps });
    }
  }

  if (activityName === 'Shuttle Run') {
    if (metrics.distance_m !== undefined) {
      formatted.push({ label: 'Total Distance (m)', value: metrics.distance_m });
    }
    if (metrics.time_sec !== undefined) {
      formatted.push({ label: 'Time Taken (s)', value: metrics.time_sec });
    }
    if (metrics.laps_completed !== undefined) {
      formatted.push({ label: 'Laps Completed', value: metrics.laps_completed });
    }
    if (metrics.avg_split_time_sec !== undefined) {
      formatted.push({ label: 'Avg Split Time (s)', value: metrics.avg_split_time_sec });
    }
  }

  if (activityName === 'Sit & Reach') {
    if (metrics.reach_cm !== undefined) {
      formatted.push({ label: 'Best Reach (cm)', value: metrics.reach_cm });
    }
    if (metrics.time_sec !== undefined) {
      formatted.push({ label: 'Attempt Time (s)', value: metrics.time_sec });
    }
  }

  if (activityName === 'Standing Broad Jump') {
    if (metrics.max_distance_m !== undefined) {
      formatted.push({ label: 'Max Distance (m)', value: metrics.max_distance_m });
    }
    if (metrics.avg_distance_m !== undefined) {
      formatted.push({ label: 'Avg Distance (m)', value: metrics.avg_distance_m });
    }
    if (metrics.total_jumps !== undefined) {
      formatted.push({ label: 'Total Jumps', value: metrics.total_jumps });
    }
  }

  return formatted;
}
