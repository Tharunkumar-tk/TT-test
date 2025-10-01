import { useEffect, useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { CircleCheck as CheckCircle, Circle as XCircle, Loader as Loader2 } from 'lucide-react';
import { checkBackendHealth } from '@/services/workoutService';

export const BackendStatus = () => {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  useEffect(() => {
    const checkStatus = async () => {
      const isHealthy = await checkBackendHealth();
      setStatus(isHealthy ? 'connected' : 'disconnected');
    };

    checkStatus();
    const interval = setInterval(checkStatus, 10000);

    return () => clearInterval(interval);
  }, []);

  if (status === 'checking') {
    return (
      <Alert className="mb-4">
        <Loader2 className="h-4 w-4 animate-spin" />
        <AlertTitle>Checking Backend</AlertTitle>
        <AlertDescription>Verifying connection to processing server...</AlertDescription>
      </Alert>
    );
  }

  if (status === 'disconnected') {
    return (
      <Alert variant="destructive" className="mb-4">
        <XCircle className="h-4 w-4" />
        <AlertTitle>Backend Offline</AlertTitle>
        <AlertDescription>
          Video processing requires the backend server. Please start it by running:
          <code className="block mt-2 p-2 bg-black/10 rounded">cd backend && ./start.sh</code>
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <Alert className="mb-4 border-green-500 text-green-700">
      <CheckCircle className="h-4 w-4" />
      <AlertTitle>Backend Connected</AlertTitle>
      <AlertDescription>Ready to process workouts offline</AlertDescription>
    </Alert>
  );
};
