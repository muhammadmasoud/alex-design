import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { api } from '@/lib/api';

interface OptimizationStatus {
  optimization_queue: {
    queued_tasks: number;
    processing_tasks: number;
    processor_running: boolean;
  };
  message: string;
  processor_running: boolean;
}

export default function OptimizationStatusCard() {
  const [status, setStatus] = useState<OptimizationStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const response = await api.get('/api/admin/optimization-status/');
      setStatus(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Error fetching optimization status:', err);
      setError('Failed to load status');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    
    // Refresh status every 5 seconds if there are pending tasks
    const interval = setInterval(() => {
      if (status && (status.optimization_queue.queued_tasks > 0 || status.optimization_queue.processing_tasks > 0)) {
        fetchStatus();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [status]);

  if (isLoading) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Image Processing</CardTitle>
          <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <p className="text-xs text-muted-foreground">Loading status...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Image Processing</CardTitle>
          <AlertCircle className="h-4 w-4 text-destructive" />
        </CardHeader>
        <CardContent>
          <p className="text-xs text-destructive">{error}</p>
        </CardContent>
      </Card>
    );
  }

  const { optimization_queue } = status!;
  const totalTasks = optimization_queue.queued_tasks + optimization_queue.processing_tasks;
  const isProcessing = totalTasks > 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">Image Processing</CardTitle>
        {isProcessing ? (
          <Loader2 className="h-4 w-4 animate-spin text-primary" />
        ) : (
          <CheckCircle className="h-4 w-4 text-green-500" />
        )}
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {/* Status Badge */}
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Status:</span>
            <Badge 
              variant={isProcessing ? "secondary" : "default"}
              className={isProcessing ? "bg-blue-100 text-blue-700" : "bg-green-100 text-green-700"}
            >
              {isProcessing ? "Processing" : "Idle"}
            </Badge>
          </div>

          {/* Task Counts */}
          {isProcessing && (
            <>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Queue:</span>
                  <span>{optimization_queue.queued_tasks} pending</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Processing:</span>
                  <span>{optimization_queue.processing_tasks} active</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Total:</span>
                  <span className="font-medium">{totalTasks} tasks</span>
                </div>
              </div>

              {/* Progress Indicator */}
              <div className="space-y-2">
                <Progress 
                  value={optimization_queue.processing_tasks > 0 ? 50 : 0} 
                  className="h-2"
                />
                <p className="text-xs text-muted-foreground text-center">
                  Optimizing images in background...
                </p>
              </div>
            </>
          )}

          {/* Processor Status */}
          <div className="flex items-center justify-between text-xs">
            <span className="text-muted-foreground">Processor:</span>
            <div className="flex items-center gap-1">
              {optimization_queue.processor_running ? (
                <>
                  <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse" />
                  <span className="text-green-600">Running</span>
                </>
              ) : (
                <>
                  <div className="h-2 w-2 bg-gray-400 rounded-full" />
                  <span className="text-muted-foreground">Stopped</span>
                </>
              )}
            </div>
          </div>

          {/* Message */}
          {!isProcessing && (
            <p className="text-xs text-muted-foreground text-center">
              All images optimized ✨
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
