import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, X, AlertCircle, CheckCircle2, Image as ImageIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { validateFiles, formatFileSize, getFilePreview, ValidationResult } from '@/lib/fileValidation';

interface FileUploadProps {
  onFilesChange: (files: File[]) => void;
  multiple?: boolean;
  maxSize?: number;
  allowedTypes?: string[];
  maxFiles?: number;
  className?: string;
  accept?: string;
  disabled?: boolean;
  showPreview?: boolean;
  compress?: boolean;
}

interface FileWithPreview extends File {
  preview?: string;
  id: string;
}

export default function FileUpload({
  onFilesChange,
  multiple = false,
  maxSize = 25 * 1024 * 1024, // 25MB
  allowedTypes,
  maxFiles = 10,
  className,
  accept = "image/*,.jpg,.jpeg,.png,.gif,.bmp,.webp,.svg,.tiff,.tif,.heic,.heif",
  disabled = false,
  showPreview = true,
  compress = false
}: FileUploadProps) {
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [validation, setValidation] = useState<ValidationResult>({ valid: true, errors: [] });
  const [isDragOver, setIsDragOver] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const processFiles = async (selectedFiles: FileList | File[]) => {
    setIsProcessing(true);
    setProgress(0);

    const fileArray = Array.from(selectedFiles);
    const validationResult = validateFiles(fileArray, { maxSize, allowedTypes, maxFiles });
    setValidation(validationResult);

    if (!validationResult.valid) {
      setIsProcessing(false);
      return;
    }

    try {
      const processedFiles: FileWithPreview[] = [];
      
      for (let i = 0; i < fileArray.length; i++) {
        const file = fileArray[i];
        setProgress(((i + 1) / fileArray.length) * 100);

        const fileWithPreview: FileWithPreview = Object.assign(file, {
          id: `${file.name}-${Date.now()}-${i}`,
        });

        // Generate preview for images
        if (showPreview && file.type.startsWith('image/')) {
          try {
            fileWithPreview.preview = await getFilePreview(file);
          } catch (error) {
            console.warn('Failed to generate preview for', file.name);
          }
        }

        processedFiles.push(fileWithPreview);
      }

      const newFiles = multiple ? [...files, ...processedFiles] : processedFiles;
      setFiles(newFiles);
      onFilesChange(newFiles);

    } catch (error) {
      console.error('Error processing files:', error);
      setValidation({
        valid: false,
        errors: ['Error processing files. Please try again.']
      });
    } finally {
      setIsProcessing(false);
      setProgress(0);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (disabled) return;
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      processFiles(droppedFiles);
    }
  };

  const handleFileSelect = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = e.target.files;
    if (selectedFiles && selectedFiles.length > 0) {
      processFiles(selectedFiles);
    }
  };

  const removeFile = (fileId: string) => {
    const updatedFiles = files.filter(f => f.id !== fileId);
    setFiles(updatedFiles);
    onFilesChange(updatedFiles);
    setValidation({ valid: true, errors: [] });
  };

  const clearFiles = () => {
    setFiles([]);
    onFilesChange([]);
    setValidation({ valid: true, errors: [] });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className={cn("space-y-4", className)}>
      {/* Upload Area */}
      <div
        className={cn(
          "relative border-2 border-dashed rounded-lg p-6 transition-colors",
          isDragOver && !disabled && "border-primary bg-primary/5",
          !isDragOver && "border-muted-foreground/25 hover:border-muted-foreground/50",
          disabled && "opacity-50 cursor-not-allowed",
          !validation.valid && "border-destructive"
        )}
        onDrop={handleDrop}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
      >
        <div className="text-center">
          <Upload className={cn(
            "mx-auto h-12 w-12 text-muted-foreground mb-4",
            isDragOver && "text-primary"
          )} />
          
          <div className="space-y-2">
            <p className="text-sm font-medium">
              {isDragOver ? 'Drop files here' : 'Drag & drop files here'}
            </p>
            <p className="text-xs text-muted-foreground">
              or click to browse files
            </p>
            <div className="text-xs text-muted-foreground space-y-1">
              <p>Max size: {formatFileSize(maxSize)}</p>
              {multiple && <p>Max files: {maxFiles}</p>}
            </div>
          </div>

          <Button
            type="button"
            variant="outline"
            className="mt-4"
            disabled={disabled}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload className="mr-2 h-4 w-4" />
            Choose Files
          </Button>

          <input
            ref={fileInputRef}
            type="file"
            multiple={multiple}
            accept={accept}
            onChange={handleFileSelect}
            disabled={disabled}
            className="hidden"
          />
        </div>
      </div>

      {/* Processing Progress */}
      {isProcessing && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span>Processing files...</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>
      )}

      {/* Validation Errors */}
      {!validation.valid && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            <ul className="space-y-1">
              {validation.errors.map((error, index) => (
                <li key={index}>{error}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">
              Selected Files ({files.length})
            </h4>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={clearFiles}
            >
              Clear All
            </Button>
          </div>

          <div className="grid gap-3">
            {files.map((file) => (
              <div
                key={file.id}
                className="flex items-center space-x-3 p-3 border rounded-lg bg-muted/30"
              >
                {/* Preview */}
                {showPreview && file.preview ? (
                  <div className="flex-shrink-0">
                    <img
                      src={file.preview}
                      alt={file.name}
                      className="h-12 w-12 object-cover rounded"
                    />
                  </div>
                ) : (
                  <div className="flex-shrink-0">
                    <ImageIcon className="h-12 w-12 text-muted-foreground" />
                  </div>
                )}

                {/* File Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <Badge variant="secondary" className="text-xs">
                      {formatFileSize(file.size)}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {file.type}
                    </Badge>
                  </div>
                </div>

                {/* Status & Actions */}
                <div className="flex items-center space-x-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(file.id)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
