// ABOUTME: CSV file processing screen with real-time progress updates
// ABOUTME: Shows upload progress, processing status, and transitions to chat interface

import React, { useState, useEffect } from 'react';
import {
  Upload,
  FileSpreadsheet,
  CheckCircle,
  AlertCircle,
  Loader2,
  ArrowRight,
  Database,
  Zap
} from 'lucide-react';
import { Button } from '../ui/Button';
import { UploadedFile } from '../../types';

interface ProcessingScreenProps {
  file: UploadedFile;
  onComplete: () => void;
  onError: (error: string) => void;
}

interface ProcessingStep {
  id: string;
  label: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress?: number;
  description: string;
}

export function ProcessingScreen({ file, onComplete, onError }: ProcessingScreenProps) {
  const [steps, setSteps] = useState<ProcessingStep[]>([
    {
      id: 'upload',
      label: 'File Upload',
      status: 'completed',
      progress: 100,
      description: 'CSV file uploaded successfully'
    },
    {
      id: 'validation',
      label: 'File Validation',
      status: 'processing',
      progress: 0,
      description: 'Validating CSV format and structure'
    },
    {
      id: 'conversion',
      label: 'Database Conversion',
      status: 'pending',
      progress: 0,
      description: 'Converting CSV to SQLite database'
    },
    {
      id: 'schema',
      label: 'Schema Detection',
      status: 'pending',
      progress: 0,
      description: 'Analyzing columns and data types'
    },
    {
      id: 'optimization',
      label: 'Query Optimization',
      status: 'pending',
      progress: 0,
      description: 'Preparing database for fast queries'
    }
  ]);

  const [currentStepIndex, setCurrentStepIndex] = useState(1);
  const [overallProgress, setOverallProgress] = useState(20);

  useEffect(() => {
    // Simulate processing steps
    const processSteps = async () => {
      for (let i = 1; i < steps.length; i++) {
        await simulateStep(i);
      }

      // Complete processing
      setTimeout(() => {
        onComplete();
      }, 1000);
    };

    processSteps();
  }, []);

  const simulateStep = (stepIndex: number): Promise<void> => {
    return new Promise((resolve) => {
      setCurrentStepIndex(stepIndex);

      // Update step to processing
      setSteps(prev => prev.map((step, index) =>
        index === stepIndex
          ? { ...step, status: 'processing', progress: 0 }
          : step
      ));

      // Simulate progress
      let progress = 0;
      const interval = setInterval(() => {
        progress += Math.random() * 25 + 5; // Random progress increment

        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);

          // Mark step as completed
          setSteps(prev => prev.map((step, index) =>
            index === stepIndex
              ? { ...step, status: 'completed', progress: 100 }
              : step
          ));

          // Update overall progress
          setOverallProgress(((stepIndex + 1) / steps.length) * 100);

          resolve();
        } else {
          // Update step progress
          setSteps(prev => prev.map((step, index) =>
            index === stepIndex
              ? { ...step, progress }
              : step
          ));

          // Update overall progress
          const baseProgress = (stepIndex / steps.length) * 100;
          const stepProgress = (progress / 100) * (100 / steps.length);
          setOverallProgress(baseProgress + stepProgress);
        }
      }, 200);
    });
  };

  const getStepIcon = (step: ProcessingStep) => {
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-success" />;
      case 'processing':
        return <Loader2 className="h-5 w-5 text-blue-primary animate-spin" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-error" />;
      default:
        return <div className="h-5 w-5 rounded-full border-2 border-surface bg-secondary-dark" />;
    }
  };

  return (
    <div className="min-h-screen bg-secondary-dark flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <FileSpreadsheet className="h-16 w-16 text-blue-primary" />
              <div className="absolute -top-2 -right-2 bg-blue-primary rounded-full p-1">
                <Zap className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>

          <h1 className="text-2xl font-bold text-light-primary mb-2">
            Processing Your Data
          </h1>
          <p className="text-light-muted">
            We're preparing <span className="font-medium text-light-primary">{file.name}</span> for analysis
          </p>
        </div>

        {/* Overall Progress */}
        <div className="bg-surface rounded-lg p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-light-primary">Overall Progress</span>
            <span className="text-sm text-light-muted">{Math.round(overallProgress)}%</span>
          </div>

          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${overallProgress}%` }}
            />
          </div>
        </div>

        {/* Processing Steps */}
        <div className="bg-surface rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-light-primary mb-4 flex items-center gap-2">
            <Database className="h-5 w-5" />
            Processing Steps
          </h3>

          <div className="space-y-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-start gap-4">
                <div className="flex-shrink-0 mt-0.5">
                  {getStepIcon(step)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-sm font-medium text-light-primary">
                      {step.label}
                    </h4>
                    {step.status === 'processing' && step.progress !== undefined && (
                      <span className="text-xs text-light-muted">
                        {Math.round(step.progress)}%
                      </span>
                    )}
                  </div>

                  <p className="text-xs text-light-muted mb-2">
                    {step.description}
                  </p>

                  {step.status === 'processing' && step.progress !== undefined && (
                    <div className="progress-bar h-1">
                      <div
                        className="progress-fill"
                        style={{ width: `${step.progress}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* File Info */}
        <div className="bg-surface/50 rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-xs text-light-subtle mb-1">File Size</div>
              <div className="text-sm font-medium text-light-primary">
                {(file.size / 1024 / 1024).toFixed(1)} MB
              </div>
            </div>
            <div>
              <div className="text-xs text-light-subtle mb-1">Format</div>
              <div className="text-sm font-medium text-light-primary">CSV</div>
            </div>
            <div>
              <div className="text-xs text-light-subtle mb-1">Estimated Rows</div>
              <div className="text-sm font-medium text-light-primary">
                {file.estimatedRows?.toLocaleString() || 'Calculating...'}
              </div>
            </div>
            <div>
              <div className="text-xs text-light-subtle mb-1">Status</div>
              <div className="text-sm font-medium text-blue-primary">Processing</div>
            </div>
          </div>
        </div>

        {/* Loading Animation */}
        <div className="text-center mt-8">
          <div className="inline-flex items-center gap-2 text-light-muted">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">This usually takes 30-60 seconds...</span>
          </div>
        </div>
      </div>
    </div>
  );
}
