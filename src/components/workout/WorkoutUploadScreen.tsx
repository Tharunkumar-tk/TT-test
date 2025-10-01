import { useState, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ArrowLeft,
  Upload,
  Camera,
  Play,
  Square,
  RotateCcw
} from 'lucide-react';
import { BackendStatus } from '@/components/BackendStatus';

interface WorkoutUploadScreenProps {
  activityName: string;
  onBack: () => void;
  onVideoSelected: (file: File) => void;
}

const WorkoutUploadScreen = ({ activityName, onBack, onVideoSelected }: WorkoutUploadScreenProps) => {
  const [mode, setMode] = useState<'selection' | 'recording'>('selection');
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [recordedBlob, setRecordedBlob] = useState<Blob | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recordingTimerRef = useRef<NodeJS.Timeout | null>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type.startsWith('video/')) {
      onVideoSelected(file);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: 'user' }, 
        audio: false 
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      setMode('recording');
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Unable to access camera. Please check permissions.');
    }
  };

  const startRecording = () => {
    if (!streamRef.current) return;

    const mediaRecorder = new MediaRecorder(streamRef.current);
    mediaRecorderRef.current = mediaRecorder;
    const chunks: BlobPart[] = [];

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        chunks.push(event.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunks, { type: 'video/webm' });
      setRecordedBlob(blob);
    };

    mediaRecorder.start();
    setIsRecording(true);
    setRecordingTime(0);

    // Start timer
    recordingTimerRef.current = setInterval(() => {
      setRecordingTime(prev => prev + 1);
    }, 1000);

    // Auto-stop after 60 seconds
    setTimeout(() => {
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        stopRecording();
      }
    }, 60000);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }
    }
  };

  const useRecording = () => {
    if (recordedBlob) {
      // Create a File object from the blob with a filename that starts with 'g' for good posture
      const file = new File([recordedBlob], `grecorded-${Date.now()}.webm`, { type: 'video/webm' });
      onVideoSelected(file);
    }
  };

  const retryRecording = () => {
    setRecordedBlob(null);
    setRecordingTime(0);
    startCamera();
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
    }
    setMode('selection');
    setRecordedBlob(null);
    setRecordingTime(0);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Recording Mode
  if (mode === 'recording') {
    return (
      <div className="min-h-screen bg-black flex flex-col">
        {/* Camera View */}
        <div className="flex-1 relative">
          <video
            ref={videoRef}
            autoPlay
            muted
            playsInline
            className="w-full h-full object-cover"
          />

          {/* Recording Indicator */}
          {isRecording && (
            <div className="absolute top-6 left-6 bg-red-500 text-white px-3 py-1 rounded-full flex items-center space-x-2">
              <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
              <span className="font-mono text-sm">{formatTime(recordingTime)}</span>
            </div>
          )}

          {/* Instructions */}
          <div className="absolute top-6 right-6 bg-black/70 text-white p-3 rounded-lg max-w-xs">
            <p className="text-sm">Keep device steady</p>
            <p className="text-xs opacity-80">Full body in frame</p>
            <p className="text-xs opacity-80">Good lighting required</p>
          </div>

          {/* Recording Preview (if recorded) */}
          {recordedBlob && !isRecording && (
            <div className="absolute inset-0 bg-black/80 flex items-center justify-center">
              <div className="text-center text-white space-y-4">
                <div className="text-6xl">✅</div>
                <h2 className="text-xl font-bold">Recording Complete!</h2>
                <p className="text-sm opacity-80">Duration: {formatTime(recordingTime)}</p>
              </div>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="p-6 bg-black safe-bottom">
          <div className="flex justify-center items-center space-x-6">
            <Button
              variant="outline"
              size="lg"
              onClick={stopCamera}
              className="bg-white/10 border-white/20 text-white hover:bg-white/20"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back
            </Button>

            {!recordedBlob ? (
              <Button
                size="lg"
                onClick={isRecording ? stopRecording : startRecording}
                className={`${isRecording ? 'bg-red-500 hover:bg-red-600' : 'bg-primary hover:bg-primary-dark'} text-white px-8`}
              >
                {isRecording ? (
                  <>
                    <Square className="w-5 h-5 mr-2" />
                    Stop
                  </>
                ) : (
                  <>
                    <Camera className="w-5 h-5 mr-2" />
                    Record
                  </>
                )}
              </Button>
            ) : (
              <div className="flex space-x-3">
                <Button
                  variant="outline"
                  size="lg"
                  onClick={retryRecording}
                  className="bg-white/10 border-white/20 text-white hover:bg-white/20"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Retry
                </Button>
                <Button
                  size="lg"
                  onClick={useRecording}
                  className="bg-success hover:bg-success/90 text-white px-8"
                >
                  <Play className="w-5 h-5 mr-2" />
                  Use Recording
                </Button>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Selection Mode
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="sticky top-0 z-50 bg-background/80 backdrop-blur-subtle border-b safe-top">
        <div className="px-4 py-4">
          <div className="flex items-center space-x-3 max-w-md mx-auto">
            <Button variant="ghost" size="sm" onClick={onBack} className="tap-target">
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div className="flex-1">
              <h1 className="text-lg font-semibold">Start Workout</h1>
              <p className="text-sm text-muted-foreground">{activityName}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="px-4 pb-20 max-w-md mx-auto pt-6 space-y-6">
        {/* Backend Status */}
        <BackendStatus />

        {/* Activity Overview */}
        <Card className="card-elevated">
          <CardContent className="p-6 text-center">
            <div className="text-6xl mb-4">💪</div>
            <h2 className="text-xl font-bold mb-2">{activityName}</h2>
            <p className="text-muted-foreground mb-4">Choose how to capture your workout</p>
          </CardContent>
        </Card>

        {/* Upload/Record Options */}
        <div className="space-y-4">
          <Button 
            onClick={() => fileInputRef.current?.click()}
            className="w-full h-16 btn-hero text-lg"
          >
            <Upload className="w-6 h-6 mr-3" />
            Upload Video
          </Button>
          
          <Button 
            onClick={startCamera}
            variant="outline" 
            className="w-full h-16 text-lg border-2 hover:bg-primary hover:text-primary-foreground"
          >
            <Camera className="w-6 h-6 mr-3" />
            Record Video
          </Button>
        </div>

        {/* Instructions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Tips for Best Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-sm">Ensure good lighting and clear view</p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-sm">Keep your full body in frame</p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-sm">Maintain steady camera position</p>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0" />
              <p className="text-sm">Perform exercise with proper form</p>
            </div>
          </CardContent>
        </Card>

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="video/mp4,video/*"
          onChange={handleFileUpload}
          className="hidden"
        />
      </div>
    </div>
  );
};

export default WorkoutUploadScreen;