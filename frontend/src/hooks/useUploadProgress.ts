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
      error: null,
    });

    abortControllerRef.current = new AbortController();
    startTimeRef.current = Date.now();
    uploadedBytesRef.current = 0;

    try {
      const totalBytes = files.reduce((sum, file) => sum + file.size, 0);
      let completedFiles = 0;
      let uploadedBytes = 0;

      // Create FormData for bulk upload
      const uploadFormData = new FormData();
      
      // Copy existing form data
      for (const [key, value] of formData.entries()) {
        uploadFormData.append(key, value);
      }

      // Add all files
      files.forEach((fileObj, index) => {
        uploadFormData.append('images', fileObj.file);
      });

      // Configure axios for progress tracking
      const response = await api.post(endpoint, uploadFormData, {
        signal: abortControllerRef.current.signal,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
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
          }));
        },
      });

      // Upload completed successfully
      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        isCompleted: true,
        uploadedFiles: files.length,
        overallProgress: 100,
        currentFileProgress: 100,
      }));

      onSuccess?.(response.data);

    } catch (error: any) {
      const errorMessage = error.name === 'AbortError' 
        ? 'Upload cancelled' 
        : error.response?.data?.detail || error.message || 'Upload failed';

      setUploadState(prev => ({
        ...prev,
        isUploading: false,
        isCompleted: true,
        error: errorMessage,
      }));

      onError?.(errorMessage);
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
