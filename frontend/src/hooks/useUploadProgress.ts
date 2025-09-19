import { useState, useCallback, useRef } from 'react';
import { api } from '@/lib/api';

export interface UploadState {
  isUploading: boolean;
  isPaused: boolean;
  isCompleted: boolean;
  totalFiles: number;
  uploadedFiles: number;
  currentFileName: string;
  currentFileProgress: number;
  overallProgress: number;
  uploadSpeed: number;
  estimatedTimeRemaining: number;
  totalBytes: number;
  uploadedBytes: number;
  remainingBytes: number;
  error: string | null;
}

export interface UploadFile {
  file: File;
  name: string;
  size: number;
}

export function useUploadProgress() {
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    isPaused: false,
    isCompleted: false,
    totalFiles: 0,
    uploadedFiles: 0,
    currentFileName: '',
    currentFileProgress: 0,
    overallProgress: 0,
    uploadSpeed: 0,
    estimatedTimeRemaining: 0,
    totalBytes: 0,
    uploadedBytes: 0,
    remainingBytes: 0,
    error: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const startTimeRef = useRef<number>(0);
  const uploadedBytesRef = useRef<number>(0);
  const isPausedRef = useRef<boolean>(false);

  const calculateProgress = useCallback((completed: number, total: number, currentProgress: number) => {
    const completedFilesProgress = (completed / total) * 100;
    const currentFileContribution = (currentProgress / total);
    return Math.min(completedFilesProgress + currentFileContribution, 100);
  }, []);

  const calculateSpeed = useCallback((uploadedBytes: number, elapsedTime: number) => {
    if (elapsedTime === 0) return 0;
    return uploadedBytes / (elapsedTime / 1000); // bytes per second
  }, []);

  const calculateETA = useCallback((remainingBytes: number, speed: number) => {
    if (speed === 0) return 0;
    return remainingBytes / speed; // seconds
  }, []);

  const uploadFiles = useCallback(async (
    files: UploadFile[],
    endpoint: string,
    formData: FormData,
    onSuccess?: (data: any) => void,
    onError?: (error: string) => void
  ) => {
    if (files.length === 0) return;

    const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
    
    // Reset state
    setUploadState({
      isUploading: true,
      isPaused: false,
      isCompleted: false,
      totalFiles: files.length,
      uploadedFiles: 0,
      currentFileName: '',
      currentFileProgress: 0,
      overallProgress: 0,
      uploadSpeed: 0,
      estimatedTimeRemaining: 0,
      totalBytes,
      uploadedBytes: 0,
      remainingBytes: totalBytes,
      error: null,
    });

    abortControllerRef.current = new AbortController();
    startTimeRef.current = Date.now();
    uploadedBytesRef.current = 0;

    try {
      // Create FormData for bulk upload
      const uploadFormData = new FormData();
      
      // Copy existing form data
      for (const [key, value] of formData.entries()) {
        uploadFormData.append(key, value);
      }

      // Add all files
      files.forEach((fileObj) => {
        uploadFormData.append('images', fileObj.file);
      });

      // Log upload start for debugging in development only
      if (process.env.NODE_ENV === 'development') {
        console.log(`Starting upload to ${endpoint} with ${files.length} files`);
      }

      // Configure axios for progress tracking with better error handling
      const response = await api.post(endpoint, uploadFormData, {
        signal: abortControllerRef.current.signal,
        timeout: 1200000, // 20 minutes timeout specifically for large uploads
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        // Add retry logic for network issues
        validateStatus: (status) => status < 500, // Don't retry on server errors
        maxRedirects: 0, // Don't follow redirects
        onUploadProgress: (progressEvent) => {
          if (isPausedRef.current) return;

          const { loaded, total } = progressEvent;
          if (!total) return;

          const currentProgress = (loaded / total) * 100;
          const overallProgress = currentProgress;
          const elapsedTime = Date.now() - startTimeRef.current;
          const speed = calculateSpeed(loaded, elapsedTime);
          const remainingBytes = total - loaded;
          const eta = calculateETA(remainingBytes, speed);

          // Estimate current file (approximate)
          const estimatedCurrentFile = Math.floor((loaded / total) * files.length);
          const currentFileName = files[Math.min(estimatedCurrentFile, files.length - 1)]?.name || '';

          setUploadState(prev => ({
            ...prev,
            currentFileName,
            currentFileProgress: currentProgress,
            overallProgress,
            uploadSpeed: speed,
            estimatedTimeRemaining: eta,
            totalBytes: total,
            uploadedBytes: loaded,
            remainingBytes: Math.max(0, total - loaded),
          }));
        },
      });

      if (process.env.NODE_ENV === 'development') {
        console.log('Upload response received:', {
          status: response.status,
          dataKeys: Object.keys(response.data)
        });
      }

      // Check if the response indicates success
      if (response.status >= 200 && response.status < 300) {
        // Upload completed successfully
        setUploadState(prev => ({
          ...prev,
          isUploading: false,
          isCompleted: true,
          uploadedFiles: files.length,
          overallProgress: 100,
          currentFileProgress: 100,
          uploadedBytes: prev.totalBytes,
          remainingBytes: 0,
        }));

        // Call onSuccess callback if provided
        if (onSuccess) {
          try {
            onSuccess(response.data);
          } catch (callbackError) {
            console.error('Error in onSuccess callback:', callbackError);
            // Don't treat callback errors as upload failures
            // The upload was successful, just the callback failed
          }
        }
      } else {
        // Handle unexpected response status
        throw new Error(`Unexpected response status: ${response.status} ${response.statusText}`);
      }

    } catch (error: any) {
      console.error('Upload error:', error);
      
      // Check if it's an abort error
      if (error.name === 'AbortError') {
        const errorMessage = 'Upload cancelled';
        setUploadState(prev => ({
          ...prev,
          isUploading: false,
          isCompleted: true,
          error: errorMessage,
        }));
        onError?.(errorMessage);
        return;
      }

      // Check if it's an HTTP error response
      if (error.response) {
        console.error('HTTP Error Response:', {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data
        });
        
        const errorMessage = error.response.data?.detail || 
                           error.response.data?.error || 
                           error.response.statusText || 
                           `HTTP ${error.response.status} error`;
        
        setUploadState(prev => ({
          ...prev,
          isUploading: false,
          isCompleted: true,
          error: errorMessage,
        }));
        
        onError?.(errorMessage);
      } else if (error.request) {
        // Network error - no response received
        const errorMessage = 'Network error - no response received';
        setUploadState(prev => ({
          ...prev,
          isUploading: false,
          isCompleted: true,
          error: errorMessage,
        }));
        
        onError?.(errorMessage);
      } else {
        // Other error
        const errorMessage = error.message || 'Upload failed';
        setUploadState(prev => ({
          ...prev,
          isUploading: false,
          isCompleted: true,
          error: errorMessage,
        }));
        
        onError?.(errorMessage);
      }
    }
  }, [calculateProgress, calculateSpeed, calculateETA]);

  const pauseUpload = useCallback(() => {
    isPausedRef.current = true;
    setUploadState(prev => ({ ...prev, isPaused: true }));
  }, []);

  const resumeUpload = useCallback(() => {
    isPausedRef.current = false;
    setUploadState(prev => ({ ...prev, isPaused: false }));
  }, []);

  const cancelUpload = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setUploadState(prev => ({
      ...prev,
      isUploading: false,
      isCompleted: true,
      error: 'Upload cancelled by user',
    }));
  }, []);

  const resetUpload = useCallback(() => {
    setUploadState({
      isUploading: false,
      isPaused: false,
      isCompleted: false,
      totalFiles: 0,
      uploadedFiles: 0,
      currentFileName: '',
      currentFileProgress: 0,
      overallProgress: 0,
      uploadSpeed: 0,
      estimatedTimeRemaining: 0,
      totalBytes: 0,
      uploadedBytes: 0,
      remainingBytes: 0,
      error: null,
    });
    uploadedBytesRef.current = 0;
    isPausedRef.current = false;
  }, []);

  return {
    uploadState,
    uploadFiles,
    pauseUpload,
    resumeUpload,
    cancelUpload,
    resetUpload,
  };
}
