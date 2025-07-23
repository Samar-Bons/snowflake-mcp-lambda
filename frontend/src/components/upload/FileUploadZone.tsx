// ABOUTME: File upload zone component with drag-and-drop functionality
// ABOUTME: Handles CSV file uploads with progress indication and error states

import React, { useCallback, useRef, useState } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';
import { clsx } from 'clsx';
import { FileUploadProps } from '../../types';

export function FileUploadZone({
  onUpload,
  maxSize,
  acceptedTypes,
  state,
  progress,
  error,
  className
}: FileUploadProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelection(files[0]);
    }
  }, []);

  const handleFileSelection = (file: File) => {
    // Validate file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedTypes.includes(fileExtension)) {
      return;
    }

    // Validate file size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSize) {
      return;
    }

    onUpload(file);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Don't process files if not in idle or error state
    if (state !== 'idle' && state !== 'error') {
      return;
    }
    
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelection(files[0]);
    }
  };

  const handleClick = () => {
    if (state === 'idle' || state === 'error') {
      fileInputRef.current?.click();
    }
  };

  const formatFileSize = (bytes: number): string => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  const formatAcceptedTypes = (): string => {
    return acceptedTypes.join(', ').toUpperCase();
  };

  const getStateIcon = () => {
    switch (state) {
      case 'uploading':
      case 'processing':
        return <Upload className="h-8 w-8 animate-pulse text-blue-primary" />;
      case 'success':
        return <CheckCircle className="h-8 w-8 text-success" />;
      case 'error':
        return <AlertCircle className="h-8 w-8 text-error" />;
      default:
        return <FileText className="h-8 w-8 text-light-muted" />;
    }
  };

  const getStateMessage = () => {
    switch (state) {
      case 'uploading':
        return progress 
          ? `Uploading... ${Math.round(progress.percentage)}%`
          : 'Uploading file...';
      case 'processing':
        return progress?.currentOperation || 'Processing file...';
      case 'success':
        return 'File uploaded successfully!';
      case 'error':
        return error?.message || 'Upload failed. Please try again.';
      default:
        return 'Drop your CSV file here or click to browse';
    }
  };

  const getSubMessage = () => {
    switch (state) {
      case 'uploading':
        return progress 
          ? `${formatFileSize(progress.bytesUploaded)} of ${formatFileSize(progress.totalBytes)}`
          : 'Please wait...';
      case 'processing':
        return 'Converting to database format...';
      case 'success':
        return 'Ready to start chatting!';
      case 'error':
        return error?.details || `Accepted: ${formatAcceptedTypes()} • Max size: ${maxSize}MB`;
      default:
        return `Accepted: ${formatAcceptedTypes()} • Max size: ${maxSize}MB`;
    }
  };

  const uploadZoneClasses = clsx(
    'upload-zone',
    {
      'upload-zone--drag-over': isDragOver,
      'upload-zone--uploading': state === 'uploading' || state === 'processing',
    },
    className
  );

  return (
    <div
      className={uploadZoneClasses}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={handleClick}
    >
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedTypes.join(',')}
        onChange={handleInputChange}
        className="hidden"
        disabled={state === 'uploading' || state === 'processing'}
      />

      <div className="flex flex-col items-center justify-center space-y-4 text-center">
        {getStateIcon()}
        
        <div className="space-y-2">
          <p className="text-lg font-medium text-light-primary">
            {getStateMessage()}
          </p>
          <p className="text-sm text-light-muted">
            {getSubMessage()}
          </p>
        </div>

        {/* Progress bar for upload/processing */}
        {(state === 'uploading' || state === 'processing') && progress && (
          <div className="w-full max-w-xs">
            <div className="w-full bg-surface rounded-full h-2">
              <div 
                className="progress-bar h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress.percentage}%` }}
              />
            </div>
          </div>
        )}

        {/* Trust indicators for idle state */}
        {state === 'idle' && (
          <div className="grid grid-cols-2 gap-4 text-xs text-light-subtle">
            <div className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3" />
              <span>No signup required</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3" />
              <span>Files stay private</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3" />
              <span>Up to {maxSize}MB</span>
            </div>
            <div className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3" />
              <span>Auto-deleted in 24h</span>
            </div>
          </div>
        )}

        {/* Error details */}
        {state === 'error' && error && (
          <div className="text-xs text-error bg-error/10 px-3 py-2 rounded-md">
            {error.details}
          </div>
        )}
      </div>
    </div>
  );
}