// ABOUTME: File upload service for handling CSV/Excel file validation and processing
// ABOUTME: Provides file validation, progress tracking, and upload management functionality

import { apiClient } from './api';
import { BackendAdapters } from './adapters';
import { UploadedFile, TableSchema, ApiResponse, UploadProgress } from '../types';

interface FileValidationResult {
  isValid: boolean;
  errors: string[];
}

interface ProgressTracker {
  progress: number;
  stage: 'preparing' | 'uploading' | 'processing' | 'complete' | 'error';
  message: string;
  estimatedTimeRemaining: number | null;

  updateProgress: (
    progress: number,
    stage?: ProgressTracker['stage'],
    message?: string,
    estimatedTime?: number
  ) => void;
  complete: (message?: string) => void;
  error: (message: string) => void;
}

class FileUploadService {
  private readonly MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB
  private readonly ACCEPTED_TYPES = [
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  ];
  private readonly ACCEPTED_EXTENSIONS = ['.csv', '.xlsx', '.xls'];

  /**
   * Validate a file for upload
   */
  validateFile(file: File): FileValidationResult {
    const errors: string[] = [];

    // Check file size
    if (file.size === 0) {
      errors.push('File cannot be empty');
    } else if (file.size > this.MAX_FILE_SIZE) {
      errors.push('File size must be less than 100MB');
    }

    // Check file type
    const extension = this.getFileExtension(file.name);
    const isValidType = this.ACCEPTED_TYPES.includes(file.type) ||
                       this.ACCEPTED_EXTENSIONS.includes(`.${extension}`);

    if (!isValidType) {
      errors.push('Only CSV and Excel files are supported');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Get accepted file types for input element
   */
  getAcceptedFileTypes(): string[] {
    return [...this.ACCEPTED_TYPES, ...this.ACCEPTED_EXTENSIONS];
  }

  /**
   * Format file size in human readable format
   */
  formatFileSize(bytes: number): string {
    if (bytes <= 0 || !Number.isFinite(bytes) || bytes < 1) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    // Ensure i is within bounds
    const sizeIndex = Math.min(i, sizes.length - 1);

    return (bytes / Math.pow(k, sizeIndex)).toFixed(1) + ' ' + sizes[sizeIndex];
  }

  /**
   * Estimate number of rows in a file
   */
  estimateRows(file: File): number {
    const avgBytesPerRow = file.type.includes('csv') ? 100 : 200; // Rough estimates
    return Math.max(1, Math.floor(file.size / avgBytesPerRow));
  }

  /**
   * Get file extension from filename
   */
  getFileExtension(filename: string): string {
    const lastDot = filename.lastIndexOf('.');
    return lastDot === -1 ? '' : filename.substring(lastDot + 1).toLowerCase();
  }

  /**
   * Validate CSV content structure
   */
  async isValidCSVContent(file: File): Promise<boolean> {
    return new Promise((resolve) => {
      const reader = new FileReader();

      reader.onload = (e) => {
        try {
          const text = e.target?.result as string;
          if (!text || text.trim().length === 0) {
            resolve(false);
            return;
          }

          const lines = text.trim().split('\n');
          if (lines.length < 2) {
            resolve(false); // Need at least header + 1 data row
            return;
          }

          // Check if header row exists and has content
          const header = lines[0].trim();
          if (!header || header.split(',').length < 1) {
            resolve(false);
            return;
          }

          // Basic validation - check if all rows have similar column count
          const expectedColumns = header.split(',').length;
          const isValid = lines.slice(1).every(line => {
            const columns = line.trim().split(',').length;
            return columns === expectedColumns; // Strict column count matching for CSV
          });

          resolve(isValid);
        } catch (error) {
          resolve(false);
        }
      };

      reader.onerror = () => resolve(false);
      reader.readAsText(file.slice(0, 10000)); // Read first 10KB for validation
    });
  }

  /**
   * Create a progress tracker for file upload
   */
  createProgressTracker(): ProgressTracker {
    const tracker: ProgressTracker = {
      progress: 0,
      stage: 'preparing',
      message: 'Preparing upload...',
      estimatedTimeRemaining: null,

      updateProgress(progress, stage, message, estimatedTime) {
        this.progress = Math.max(0, Math.min(100, progress));
        if (stage) this.stage = stage;
        if (message) this.message = message;
        if (estimatedTime !== undefined) this.estimatedTimeRemaining = estimatedTime;
      },

      complete(message = 'Upload completed successfully') {
        this.progress = 100;
        this.stage = 'complete';
        this.message = message;
        this.estimatedTimeRemaining = null;
      },

      error(message) {
        this.progress = 0;
        this.stage = 'error';
        this.message = message;
        this.estimatedTimeRemaining = null;
      },
    };

    return tracker;
  }

  /**
   * Calculate upload ETA based on progress
   */
  calculateETA(startTime: number, progress: number): number | null {
    if (progress <= 0) return null;

    const elapsed = Date.now() - startTime;
    const rate = progress / elapsed;
    const remaining = 100 - progress;

    return remaining / rate;
  }

  /**
   * Check if file type is supported
   */
  isFileTypeSupported(file: File): boolean {
    const extension = this.getFileExtension(file.name);
    return this.ACCEPTED_TYPES.includes(file.type) ||
           this.ACCEPTED_EXTENSIONS.includes(`.${extension}`);
  }

  /**
   * Get MIME type suggestions for unsupported files
   */
  getSupportedFileInfo(): { types: string[]; maxSize: string; examples: string[] } {
    return {
      types: ['CSV', 'Excel (.xlsx)', 'Excel (.xls)'],
      maxSize: this.formatFileSize(this.MAX_FILE_SIZE),
      examples: ['data.csv', 'spreadsheet.xlsx', 'records.xls'],
    };
  }

  /**
   * Upload file to backend and get schema information
   */
  async uploadFile(
    file: File,
    onProgress?: (progress: UploadProgress) => void
  ): Promise<ApiResponse<UploadedFile & { schema: TableSchema }>> {
    // Validate file before upload
    const validation = this.validateFile(file);
    if (!validation.isValid) {
      return {
        success: false,
        error: validation.errors.join(', '),
      };
    }

    try {
      // Convert API progress format to component progress format
      const backendResponse = await apiClient.uploadFile('/data/upload', file, (apiProgress) => {
        if (onProgress) {
          onProgress({
            percentage: apiProgress.percentage,
            currentOperation: apiProgress.percentage < 100 ? 'Uploading file...' : 'Processing file...',
            bytesUploaded: apiProgress.bytesUploaded,
            totalBytes: apiProgress.totalBytes,
          });
        }
      });

      // Adapt backend response to frontend format
      const adaptedResponse = BackendAdapters.adaptUploadResponse(backendResponse as any);

      // Store file info for session management
      if (adaptedResponse.success && adaptedResponse.data) {
        // Extract just the UploadedFile properties (without schema)
        const { schema, ...uploadedFile } = adaptedResponse.data;
        await this.storeUploadedFile(uploadedFile as UploadedFile);
      }

      return adaptedResponse;
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Upload failed',
      };
    }
  }

  /**
   * Get schema information for an uploaded file
   */
  async getSchema(fileId: string): Promise<ApiResponse<TableSchema>> {
    try {
      const backendResponse = await apiClient.get(`/data/schema/${fileId}`);
      return BackendAdapters.adaptSchemaResponse(backendResponse as any);
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch schema',
      };
    }
  }

  /**
   * Alias for getSchema() - used by components expecting old method name
   */
  async getFileSchema(fileId: string): Promise<TableSchema> {
    const response = await this.getSchema(fileId);
    if (!response.success || !response.data) {
      throw new Error(response.error || 'Failed to get schema');
    }
    return response.data;
  }

  /**
   * Estimate processing time based on file size (client-side implementation)
   */
  estimateProcessingTime(fileSize: number): string {
    // Rough estimation: ~1MB per second for CSV processing
    const estimatedSeconds = Math.max(1, Math.floor(fileSize / (1024 * 1024)));

    if (estimatedSeconds < 60) {
      return `${estimatedSeconds} second${estimatedSeconds === 1 ? '' : 's'}`;
    } else {
      const minutes = Math.floor(estimatedSeconds / 60);
      return `${minutes} minute${minutes === 1 ? '' : 's'}`;
    }
  }

  /**
   * Create event source for processing updates
   * MVP: Returns mock EventSource since backend doesn't provide SSE
   */
  createProcessingEventSource(fileId: string): EventSource {
    // Create a mock EventSource for MVP - in real app this would be apiClient.createEventSource()
    const mockEventSource = {
      onmessage: null as ((event: any) => void) | null,
      onerror: null as ((event: any) => void) | null,
      onopen: null as ((event: any) => void) | null,
      close: () => {},
      addEventListener: () => {},
      removeEventListener: () => {},
      dispatchEvent: () => false,
      readyState: 1, // EventSource.OPEN
      url: `/api/v1/processing/${fileId}/stream`,
      withCredentials: false,
      CONNECTING: 0,
      OPEN: 1,
      CLOSED: 2,
    } as EventSource;

    // Simulate processing completion after a short delay
    setTimeout(() => {
      if (mockEventSource.onmessage) {
        mockEventSource.onmessage({
          data: JSON.stringify({
            type: 'complete',
            progress: 100,
            message: 'Processing completed successfully'
          })
        } as MessageEvent);
      }
    }, 2000);

    return mockEventSource;
  }

  /**
   * Get list of uploaded files for current session
   * MVP: Returns files from sessionStorage since backend doesn't persist session files
   */
  async getUploadedFiles(): Promise<UploadedFile[]> {
    try {
      // In MVP, we store recently uploaded files in sessionStorage
      const stored = sessionStorage.getItem('uploadedFiles');
      if (stored) {
        const files = JSON.parse(stored) as UploadedFile[];
        return files.filter(file => {
          // Filter out files older than 24 hours
          const age = Date.now() - new Date(file.uploadedAt).getTime();
          return age < 24 * 60 * 60 * 1000;
        });
      }
      return [];
    } catch (error) {
      console.warn('Failed to load uploaded files from storage:', error);
      return [];
    }
  }

  /**
   * Store uploaded file info in session storage
   */
  private async storeUploadedFile(uploadedFile: UploadedFile): Promise<void> {
    try {
      const existing = await this.getUploadedFiles();
      const updated = [...existing.filter(f => f.id !== uploadedFile.id), uploadedFile];
      sessionStorage.setItem('uploadedFiles', JSON.stringify(updated));
    } catch (error) {
      console.warn('Failed to store uploaded file:', error);
    }
  }

  /**
   * Delete a file from the session
   * MVP: Removes from sessionStorage only, backend handles actual deletion
   */
  async deleteFile(fileId: string): Promise<void> {
    try {
      // In a real implementation, this would call the backend API
      // await apiClient.delete(`/data/files/${fileId}`);

      // For MVP, just remove from session storage
      const existing = await this.getUploadedFiles();
      const updated = existing.filter(f => f.id !== fileId);
      sessionStorage.setItem('uploadedFiles', JSON.stringify(updated));
    } catch (error) {
      console.error('Failed to delete file:', error);
      throw error;
    }
  }
}

export const fileUploadService = new FileUploadService();
