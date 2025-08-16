import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Upload, CheckCircle, XCircle, Clock, FileImage, Pause, Play, X } from "lucide-react";

export interface UploadProgressProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  totalFiles: number;
  uploadedFiles: number;
  currentFileName?: string;
  currentFileProgress: number;
  overallProgress: number;
  uploadSpeed?: number; // bytes per second
  estimatedTimeRemaining?: number; // seconds
  totalBytes?: number; // total bytes to upload
  uploadedBytes?: number; // bytes uploaded so far
  remainingBytes?: number; // bytes remaining
  error?: string;
  isCompleted: boolean;
  isPaused?: boolean;
  onPause?: () => void;
  onResume?: () => void;
  onCancel?: () => void;
}

export default function UploadProgress({
  isOpen,
  onClose,
  title,
  totalFiles,
  uploadedFiles,
  currentFileName,
  currentFileProgress,
  overallProgress,
  uploadSpeed,
  estimatedTimeRemaining,
  totalBytes,
  uploadedBytes,
  remainingBytes,
  error,
  isCompleted,
  isPaused = false,
  onPause,
  onResume,
  onCancel
}: UploadProgressProps) {
  const [showDetails, setShowDetails] = useState(false);

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (seconds: number) => {
    if (!seconds || seconds === Infinity || isNaN(seconds)) return 'Calculating...';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4"
      >
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="w-full max-w-md"
        >
          <Card className="shadow-2xl border-2">
            <CardContent className="p-6">
              {/* Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  {isCompleted ? (
                    error ? (
                      <XCircle className="h-6 w-6 text-destructive" />
                    ) : (
                      <CheckCircle className="h-6 w-6 text-green-500" />
                    )
                  ) : (
                    <Upload className="h-6 w-6 text-primary animate-pulse" />
                  )}
                  <h3 className="text-lg font-semibold">{title}</h3>
                </div>
                
                {isCompleted && (
                  <Button variant="ghost" size="sm" onClick={onClose}>
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>

              {/* Error Message */}
              {error && (
                <div className="mb-4 p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
                  <p className="text-sm text-destructive">{error}</p>
                </div>
              )}

              {/* Overall Progress */}
              <div className="space-y-3 mb-4">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground">
                    {uploadedFiles} of {totalFiles} files
                  </span>
                  <span className="font-medium">{Math.round(overallProgress)}%</span>
                </div>
                
                <Progress value={overallProgress} className="h-3" />
              </div>

              {/* Current File Progress */}
              {!isCompleted && currentFileName && (
                <div className="space-y-2 mb-4 p-3 bg-muted/30 rounded-lg">
                  <div className="flex items-center gap-2">
                    <FileImage className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm font-medium truncate flex-1">
                      {currentFileName}
                    </span>
                  </div>
                  
                  <div className="flex justify-between items-center text-xs text-muted-foreground">
                    <span>Current file</span>
                    <span>{Math.round(currentFileProgress)}%</span>
                  </div>
                  
                  <Progress value={currentFileProgress} className="h-2" />
                </div>
              )}

              {/* Upload Statistics */}
              <div className="space-y-2 mb-4">
                {/* Data Transfer Information */}
                {(uploadedBytes !== undefined && totalBytes !== undefined) && (
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Data Transfer:</span>
                    <span className="font-medium">
                      {formatFileSize(uploadedBytes)} / {formatFileSize(totalBytes)}
                    </span>
                  </div>
                )}
                
                {remainingBytes !== undefined && remainingBytes > 0 && !isCompleted && (
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Remaining:</span>
                    <span className="font-medium text-orange-500">{formatFileSize(remainingBytes)}</span>
                  </div>
                )}
                
                {uploadSpeed && (
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Upload Speed:</span>
                    <span className="font-medium text-green-500">{formatFileSize(uploadSpeed)}/s</span>
                  </div>
                )}
                
                {estimatedTimeRemaining && !isCompleted && (
                  <div className="flex justify-between items-center text-sm">
                    <div className="flex items-center gap-1">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      <span className="text-muted-foreground">Time Remaining:</span>
                    </div>
                    <span className="font-medium text-blue-500">{formatTime(estimatedTimeRemaining)}</span>
                  </div>
                )}
              </div>

              {/* Toggle Details */}
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowDetails(!showDetails)}
                className="w-full mb-4 text-xs"
              >
                {showDetails ? 'Hide Details' : 'Show Details'}
              </Button>

              {/* Detailed Stats */}
              <AnimatePresence>
                {showDetails && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: 'auto', opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    className="overflow-hidden"
                  >
                    <div className="space-y-1 text-xs text-muted-foreground bg-muted/20 p-3 rounded-lg mb-4">
                      <div className="flex justify-between">
                        <span>Files Completed:</span>
                        <span>{uploadedFiles}/{totalFiles}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Overall Progress:</span>
                        <span>{overallProgress.toFixed(1)}%</span>
                      </div>
                      {currentFileProgress > 0 && (
                        <div className="flex justify-between">
                          <span>Current File:</span>
                          <span>{currentFileProgress.toFixed(1)}%</span>
                        </div>
                      )}
                      {(uploadedBytes !== undefined && totalBytes !== undefined) && (
                        <>
                          <div className="flex justify-between">
                            <span>Data Uploaded:</span>
                            <span className="text-green-500">{formatFileSize(uploadedBytes)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Total Size:</span>
                            <span>{formatFileSize(totalBytes)}</span>
                          </div>
                          {remainingBytes !== undefined && (
                            <div className="flex justify-between">
                              <span>Remaining:</span>
                              <span className="text-orange-500">{formatFileSize(remainingBytes)}</span>
                            </div>
                          )}
                        </>
                      )}
                      {uploadSpeed && (
                        <div className="flex justify-between">
                          <span>Transfer Rate:</span>
                          <span className="text-blue-500">{formatFileSize(uploadSpeed)}/s</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span>Status:</span>
                        <span className={isCompleted ? (error ? 'text-destructive' : 'text-green-500') : isPaused ? 'text-yellow-500' : 'text-blue-500'}>
                          {isCompleted ? (error ? 'Failed' : 'Completed') : isPaused ? 'Paused' : 'Uploading'}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Control Buttons */}
              {!isCompleted && (
                <div className="flex gap-2">
                  {onPause && onResume && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={isPaused ? onResume : onPause}
                      className="flex-1"
                    >
                      {isPaused ? (
                        <>
                          <Play className="h-4 w-4 mr-1" />
                          Resume
                        </>
                      ) : (
                        <>
                          <Pause className="h-4 w-4 mr-1" />
                          Pause
                        </>
                      )}
                    </Button>
                  )}
                  
                  {onCancel && (
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={onCancel}
                      className="flex-1"
                    >
                      Cancel
                    </Button>
                  )}
                </div>
              )}

              {/* Completion Actions */}
              {isCompleted && !error && (
                <div className="flex gap-2">
                  <Button onClick={onClose} className="flex-1">
                    Done
                  </Button>
                </div>
              )}

              {/* Error Actions */}
              {isCompleted && error && (
                <div className="flex gap-2">
                  <Button variant="outline" onClick={onClose} className="flex-1">
                    Close
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
