// ABOUTME: Landing page with hero section and CSV upload functionality
// ABOUTME: Implements the complete upload flow from drag-drop to processing to chat redirect

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Database, MessageSquare, Zap } from 'lucide-react';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { Button } from '../components/ui/Button';
import { FileUploadZone } from '../components/upload/FileUploadZone';
import { fileUploadService } from '../services/fileUpload';
import { UploadProgress, FileUploadError } from '../types';

interface LandingPageProps {
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export function LandingPage({ theme, onToggleTheme }: LandingPageProps) {
  const navigate = useNavigate();
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>();
  const [uploadError, setUploadError] = useState<FileUploadError>();
  const [currentFile, setCurrentFile] = useState<File>();

  const handleFileUpload = async (file: File) => {
    setCurrentFile(file);
    setUploadState('uploading');
    setUploadError(undefined);

    try {
      // Validate file first
      const validation = fileUploadService.validateFile(file);
      if (!validation.isValid) {
        setUploadError({
          code: 'INVALID_FORMAT',
          message: 'Invalid file',
          details: validation.errors.join(', '),
        });
        setUploadState('error');
        return;
      }

      // Upload file with progress tracking
      const uploadResponse = await fileUploadService.uploadFile(
        file,
        (progress) => {
          setUploadProgress({
            ...progress,
            currentOperation: 'Uploading file...',
          });
        }
      );

      // Switch to processing state
      setUploadState('processing');
      setUploadProgress({
        percentage: 0,
        currentOperation: 'Converting to database format...',
        bytesUploaded: file.size,
        totalBytes: file.size,
      });

      // File is already processed by backend, no need for EventSource
      if (!uploadResponse.success || !uploadResponse.data) {
        throw new Error(uploadResponse.error || 'Upload failed');
      }

      setUploadState('success');

      // Show success state briefly before redirecting
      setTimeout(() => {
        navigate(`/chat/${uploadResponse.data!.id}`);
      }, 1500);

    } catch (error) {
      console.error('Upload failed:', error);
      setUploadError({
        code: 'NETWORK_ERROR',
        message: 'Upload failed',
        details: error instanceof Error ? error.message : 'Unknown error occurred',
      });
      setUploadState('error');
    }
  };

  const handleTrySample = async () => {
    try {
      // Create a sample CSV data
      const sampleCsvContent = `customer_id,name,email,age,city,purchase_amount,purchase_date
1,John Doe,john.doe@email.com,28,New York,150.50,2024-01-15
2,Jane Smith,jane.smith@email.com,34,Los Angeles,89.99,2024-01-16
3,Mike Johnson,mike.johnson@email.com,42,Chicago,210.75,2024-01-17
4,Sarah Wilson,sarah.wilson@email.com,29,Houston,45.99,2024-01-18
5,David Brown,david.brown@email.com,35,Phoenix,320.00,2024-01-19
6,Lisa Garcia,lisa.garcia@email.com,27,Philadelphia,125.50,2024-01-20
7,Robert Taylor,robert.taylor@email.com,38,San Antonio,199.99,2024-01-21
8,Emily Davis,emily.davis@email.com,31,San Diego,75.25,2024-01-22
9,Michael Miller,michael.miller@email.com,45,Dallas,410.80,2024-01-23
10,Jessica Wilson,jessica.wilson@email.com,26,San Jose,95.75,2024-01-24`;

      // Create a File object from the CSV content
      const blob = new Blob([sampleCsvContent], { type: 'text/csv' });
      const sampleFile = new File([blob], 'sample_customer_data.csv', { type: 'text/csv' });

      // Use the existing file upload handler
      await handleFileUpload(sampleFile);
    } catch (error) {
      console.error('Failed to load sample data:', error);
      setUploadError({
        code: 'SAMPLE_LOAD_ERROR',
        message: 'Failed to load sample data',
        details: error instanceof Error ? error.message : 'Unknown error occurred',
      });
      setUploadState('error');
    }
  };

  const handleRetry = () => {
    setUploadState('idle');
    setUploadError(undefined);
    setUploadProgress(undefined);
    setCurrentFile(undefined);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary to-secondary overflow-hidden">
      {/* Theme Toggle */}
      <ThemeToggle
        theme={theme}
        onToggle={onToggleTheme}
        variant="hero"
      />

      {/* Background Decorations */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-48 h-48 bg-blue-primary/10 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-60 right-15 w-32 h-32 bg-purple-primary/10 rounded-full blur-2xl animate-pulse delay-1000" />
        <div className="absolute bottom-30 left-20 w-24 h-24 bg-blue-light/10 rounded-full blur-xl animate-pulse delay-2000" />
      </div>

      {/* Main Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center px-4">
        <div className="max-w-4xl mx-auto text-center space-y-12">

          {/* Hero Title */}
          <div className="space-y-6 animate fade-in">
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-gradient leading-tight">
              Chat with Your CSV Data
            </h1>
            <p className="text-lg md:text-xl text-light-muted max-w-2xl mx-auto leading-relaxed">
              Upload any CSV file and ask questions in plain English.
              Get instant insights without writing SQL or complex queries.
            </p>
          </div>

          {/* Upload Zone */}
          <div className="max-w-2xl mx-auto animate-slide-up">
            <FileUploadZone
              onUpload={handleFileUpload}
              maxSize={100}
              acceptedTypes={['.csv', '.tsv']}
              state={uploadState}
              progress={uploadProgress}
              error={uploadError}
              className="min-h-[300px]"
            />

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mt-6">
              {uploadState === 'idle' && (
                <>
                  <Button
                    variant="secondary"
                    size="large"
                    onClick={handleTrySample}
                    className="flex items-center gap-2"
                  >
                    <Database className="h-5 w-5" />
                    Try Sample Data
                  </Button>
                </>
              )}

              {uploadState === 'error' && (
                <Button
                  variant="primary"
                  size="large"
                  onClick={handleRetry}
                  className="flex items-center gap-2"
                >
                  <ArrowRight className="h-5 w-5" />
                  Try Again
                </Button>
              )}

              {uploadState === 'success' && (
                <Button
                  variant="primary"
                  size="large"
                  disabled
                  className="flex items-center gap-2"
                >
                  <MessageSquare className="h-5 w-5" />
                  Redirecting to Chat...
                </Button>
              )}
            </div>
          </div>

          {/* Feature Highlights */}
          {uploadState === 'idle' && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto mt-16 animate-fade-in">
              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-blue-primary/20 rounded-full flex items-center justify-center mx-auto">
                  <Zap className="h-6 w-6 text-blue-primary" />
                </div>
                <h3 className="text-lg font-medium text-light-primary">
                  Instant Setup
                </h3>
                <p className="text-sm text-light-muted">
                  No account required. Upload your CSV and start asking questions in under 30 seconds.
                </p>
              </div>

              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-purple-primary/20 rounded-full flex items-center justify-center mx-auto">
                  <MessageSquare className="h-6 w-6 text-purple-primary" />
                </div>
                <h3 className="text-lg font-medium text-light-primary">
                  Natural Language
                </h3>
                <p className="text-sm text-light-muted">
                  Ask questions like "Show me top sales by region" - no SQL knowledge needed.
                </p>
              </div>

              <div className="text-center space-y-3">
                <div className="w-12 h-12 bg-success/20 rounded-full flex items-center justify-center mx-auto">
                  <Database className="h-6 w-6 text-success" />
                </div>
                <h3 className="text-lg font-medium text-light-primary">
                  Private & Secure
                </h3>
                <p className="text-sm text-light-muted">
                  Your data stays private and is automatically deleted after 24 hours.
                </p>
              </div>
            </div>
          )}

          {/* Processing Info */}
          {(uploadState === 'uploading' || uploadState === 'processing') && currentFile && (
            <div className="bg-surface/50 backdrop-blur-sm rounded-lg p-6 max-w-md mx-auto">
              <div className="space-y-3 text-center">
                <h3 className="text-lg font-medium text-light-primary">
                  Processing {currentFile.name}
                </h3>
                <p className="text-sm text-light-muted">
                  File size: {fileUploadService.formatFileSize(currentFile.size)}
                </p>
                <p className="text-xs text-light-subtle">
                  Estimated time: {fileUploadService.estimateProcessingTime(currentFile.size)}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
