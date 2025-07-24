// ABOUTME: Unit tests for file upload service functionality
// ABOUTME: Tests file validation, upload progress, and processing status monitoring

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fileUploadService } from '../fileUpload';
import { createMockFile } from '../../test/utils';

describe('FileUploadService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('validateFile', () => {
    it('should accept valid CSV files', () => {
      const file = createMockFile('test.csv', 1024 * 1024, 'text/csv'); // 1MB
      const result = fileUploadService.validateFile(file);

      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    it('should accept valid Excel files', () => {
      const file = createMockFile('test.xlsx', 2 * 1024 * 1024, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'); // 2MB
      const result = fileUploadService.validateFile(file);

      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual([]);
    });

    it('should reject files that are too large', () => {
      const file = createMockFile('huge.csv', 150 * 1024 * 1024, 'text/csv'); // 150MB
      const result = fileUploadService.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('File size must be less than 100MB');
    });

    it('should reject unsupported file types', () => {
      const file = createMockFile('test.txt', 1024, 'text/plain');
      const result = fileUploadService.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('Only CSV and Excel files are supported');
    });

    it('should reject empty files', () => {
      const file = createMockFile('empty.csv', 0, 'text/csv');
      const result = fileUploadService.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors).toContain('File cannot be empty');
    });

    it('should handle multiple validation errors', () => {
      const file = createMockFile('huge.txt', 150 * 1024 * 1024, 'text/plain');
      const result = fileUploadService.validateFile(file);

      expect(result.isValid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(1);
      expect(result.errors).toContain('File size must be less than 100MB');
      expect(result.errors).toContain('Only CSV and Excel files are supported');
    });
  });

  describe('getAcceptedFileTypes', () => {
    it('should return correct MIME types for file input', () => {
      const acceptedTypes = fileUploadService.getAcceptedFileTypes();

      expect(acceptedTypes).toContain('.csv');
      expect(acceptedTypes).toContain('.xlsx');
      expect(acceptedTypes).toContain('.xls');
      expect(acceptedTypes).toContain('text/csv');
      expect(acceptedTypes).toContain('application/vnd.ms-excel');
      expect(acceptedTypes).toContain('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    });
  });

  describe('formatFileSize', () => {
    it('should format bytes correctly', () => {
      expect(fileUploadService.formatFileSize(0)).toBe('0 Bytes');
      expect(fileUploadService.formatFileSize(1024)).toBe('1.0 KB');
      expect(fileUploadService.formatFileSize(1024 * 1024)).toBe('1.0 MB');
      expect(fileUploadService.formatFileSize(1024 * 1024 * 1024)).toBe('1.0 GB');
      expect(fileUploadService.formatFileSize(1536)).toBe('1.5 KB'); // 1.5 KB
      expect(fileUploadService.formatFileSize(2.5 * 1024 * 1024)).toBe('2.5 MB');
    });

    it('should handle edge cases', () => {
      expect(fileUploadService.formatFileSize(-1)).toBe('0 Bytes');
      expect(fileUploadService.formatFileSize(0.5)).toBe('0 Bytes');
    });
  });

  describe('estimateRows', () => {
    it('should estimate rows for CSV files', () => {
      const csvContent = 'id,name,email\n1,John,john@example.com\n2,Jane,jane@example.com';
      const file = new File([csvContent], 'test.csv', { type: 'text/csv' });

      const estimate = fileUploadService.estimateRows(file);

      expect(estimate).toBeGreaterThan(0);
      expect(typeof estimate).toBe('number');
    });

    it('should estimate rows for Excel files', () => {
      const file = createMockFile('test.xlsx', 50 * 1024, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');

      const estimate = fileUploadService.estimateRows(file);

      expect(estimate).toBeGreaterThan(0);
      expect(typeof estimate).toBe('number');
    });

    it('should return reasonable estimates', () => {
      const smallFile = createMockFile('small.csv', 1024, 'text/csv'); // 1KB
      const largeFile = createMockFile('large.csv', 10 * 1024 * 1024, 'text/csv'); // 10MB

      const smallEstimate = fileUploadService.estimateRows(smallFile);
      const largeEstimate = fileUploadService.estimateRows(largeFile);

      expect(largeEstimate).toBeGreaterThan(smallEstimate);
      expect(smallEstimate).toBeGreaterThan(0);
    });
  });

  describe('createProgressTracker', () => {
    it('should create a progress tracker with initial state', () => {
      const tracker = fileUploadService.createProgressTracker();

      expect(tracker.progress).toBe(0);
      expect(tracker.stage).toBe('preparing');
      expect(tracker.message).toBe('Preparing upload...');
      expect(tracker.estimatedTimeRemaining).toBeNull();
    });

    it('should allow progress updates', () => {
      const tracker = fileUploadService.createProgressTracker();

      tracker.updateProgress(50, 'uploading', 'Uploading file...', 30);

      expect(tracker.progress).toBe(50);
      expect(tracker.stage).toBe('uploading');
      expect(tracker.message).toBe('Uploading file...');
      expect(tracker.estimatedTimeRemaining).toBe(30);
    });

    it('should handle complete stage', () => {
      const tracker = fileUploadService.createProgressTracker();

      tracker.complete('File uploaded successfully');

      expect(tracker.progress).toBe(100);
      expect(tracker.stage).toBe('complete');
      expect(tracker.message).toBe('File uploaded successfully');
      expect(tracker.estimatedTimeRemaining).toBeNull();
    });

    it('should handle error stage', () => {
      const tracker = fileUploadService.createProgressTracker();

      tracker.error('Upload failed');

      expect(tracker.progress).toBe(0);
      expect(tracker.stage).toBe('error');
      expect(tracker.message).toBe('Upload failed');
      expect(tracker.estimatedTimeRemaining).toBeNull();
    });
  });

  describe('getFileExtension', () => {
    it('should extract file extensions correctly', () => {
      expect(fileUploadService.getFileExtension('test.csv')).toBe('csv');
      expect(fileUploadService.getFileExtension('data.xlsx')).toBe('xlsx');
      expect(fileUploadService.getFileExtension('file.name.with.dots.xls')).toBe('xls');
      expect(fileUploadService.getFileExtension('noextension')).toBe('');
      expect(fileUploadService.getFileExtension('')).toBe('');
    });
  });

  describe('isValidCSVContent', () => {
    it('should validate proper CSV content', async () => {
      const validCsv = 'id,name,email\n1,John,john@example.com\n2,Jane,jane@example.com';
      const file = new File([validCsv], 'test.csv', { type: 'text/csv' });

      const isValid = await fileUploadService.isValidCSVContent(file);
      expect(isValid).toBe(true);
    });

    it('should reject malformed CSV content', async () => {
      const invalidCsv = 'id,name,email\n1,John\n2,Jane,jane@example.com,extra';
      const file = new File([invalidCsv], 'test.csv', { type: 'text/csv' });

      const isValid = await fileUploadService.isValidCSVContent(file);
      expect(isValid).toBe(false);
    });

    it('should handle empty CSV files', async () => {
      const emptyCsv = '';
      const file = new File([emptyCsv], 'test.csv', { type: 'text/csv' });

      const isValid = await fileUploadService.isValidCSVContent(file);
      expect(isValid).toBe(false);
    });

    it('should handle CSV with only headers', async () => {
      const headerOnlyCsv = 'id,name,email';
      const file = new File([headerOnlyCsv], 'test.csv', { type: 'text/csv' });

      const isValid = await fileUploadService.isValidCSVContent(file);
      expect(isValid).toBe(false);
    });
  });
});
