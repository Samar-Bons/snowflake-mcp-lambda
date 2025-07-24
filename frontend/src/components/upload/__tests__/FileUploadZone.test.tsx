// ABOUTME: Unit tests for FileUploadZone component
// ABOUTME: Tests drag-drop functionality, file validation, and upload states

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '../../../test/utils';
import { FileUploadZone } from '../FileUploadZone';
import { createMockFile } from '../../../test/utils';

const mockOnUpload = vi.fn();
const mockOnError = vi.fn();

const defaultProps = {
  onUpload: mockOnUpload,
  state: 'idle' as const,
  maxSize: 100, // 100MB
  acceptedTypes: ['.csv', '.xlsx'],
};

describe('FileUploadZone', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders with idle state', () => {
    render(<FileUploadZone {...defaultProps} />);

    expect(screen.getByText(/drop your csv file here/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument();
    expect(screen.getByText(/no signup required/i)).toBeInTheDocument();
    expect(screen.getByText(/files stay private/i)).toBeInTheDocument();
  });

  it('shows uploading state correctly', () => {
    render(
      <FileUploadZone
        {...defaultProps}
        state="uploading"
        progress={{ percentage: 45, bytesUploaded: 500000, totalBytes: 1000000 }}
      />
    );

    expect(screen.getByText(/uploading\.\.\. 45%/i)).toBeInTheDocument();
    expect(screen.getByText(/0\.5 mb of 1\.0 mb/i)).toBeInTheDocument();
  });

  it('shows processing state correctly', () => {
    render(
      <FileUploadZone
        {...defaultProps}
        state="processing"
        progress={{ currentOperation: "Analyzing file structure..." }}
      />
    );

    expect(screen.getByText(/analyzing file structure/i)).toBeInTheDocument();
    expect(screen.getByText(/converting to database format/i)).toBeInTheDocument();
  });

  it('shows success state correctly', () => {
    render(
      <FileUploadZone
        {...defaultProps}
        state="success"
      />
    );

    expect(screen.getByText(/file uploaded successfully/i)).toBeInTheDocument();
    expect(screen.getByText(/ready to start chatting/i)).toBeInTheDocument();
  });

  it('shows error state correctly', () => {
    render(
      <FileUploadZone
        {...defaultProps}
        state="error"
        error={{ message: "File too large", details: "Maximum file size is 100MB" }}
      />
    );

    expect(screen.getByText(/file too large/i)).toBeInTheDocument();
    expect(screen.getAllByText(/maximum file size is 100mb/i)).toHaveLength(2); // Appears in both submessage and error details
  });

  it('handles file selection via click', async () => {
    render(<FileUploadZone {...defaultProps} />);

    const uploadZone = screen.getByText(/drop your csv file here/i).closest('.upload-zone');
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement; // File input with hidden class
    const file = createMockFile('test.csv', 1024, 'text/csv');

    expect(uploadZone).toBeInTheDocument();

    // Simulate file selection by directly triggering the change event
    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalledWith(file);
    });
  });

  it('handles drag and drop events', () => {
    render(<FileUploadZone {...defaultProps} />);

    const uploadZone = screen.getByText(/drop your csv file here/i).closest('.upload-zone') as HTMLElement;
    const file = createMockFile('test.csv', 1024, 'text/csv');

    // Test drag over (this is what actually triggers the state change)
    fireEvent.dragOver(uploadZone, {
      dataTransfer: {
        items: [{ kind: 'file', type: 'text/csv' }],
      },
    });

    expect(uploadZone).toHaveClass('upload-zone--drag-over');

    // Test drag leave
    fireEvent.dragLeave(uploadZone);
    expect(uploadZone).not.toHaveClass('upload-zone--drag-over');

    // Test drop
    fireEvent.drop(uploadZone, {
      dataTransfer: {
        files: [file],
      },
    });
  });

  it('validates files on upload', async () => {
    render(<FileUploadZone {...defaultProps} />);

    const uploadZone = screen.getByText(/drop your csv file here/i).closest('.upload-zone') as HTMLElement;

    // Test with invalid file type - should not call onUpload
    const invalidFile = createMockFile('test.txt', 1024, 'text/plain');
    fireEvent.drop(uploadZone, {
      dataTransfer: {
        files: [invalidFile],
      },
    });

    await waitFor(() => {
      expect(mockOnUpload).not.toHaveBeenCalled();
    });
  });

  it('validates file size', async () => {
    render(<FileUploadZone {...defaultProps} />);

    const uploadZone = screen.getByText(/drop your csv file here/i).closest('.upload-zone') as HTMLElement;

    // Test with oversized file - should not call onUpload
    const largeFile = createMockFile('huge.csv', 200 * 1024 * 1024, 'text/csv'); // 200MB
    fireEvent.drop(uploadZone, {
      dataTransfer: {
        files: [largeFile],
      },
    });

    await waitFor(() => {
      expect(mockOnUpload).not.toHaveBeenCalled();
    });
  });

  it('calls onUpload with valid file', async () => {
    render(<FileUploadZone {...defaultProps} />);

    const uploadZone = screen.getByText(/drop your csv file here/i).closest('.upload-zone') as HTMLElement;
    const validFile = createMockFile('test.csv', 1024, 'text/csv');

    fireEvent.drop(uploadZone, {
      dataTransfer: {
        files: [validFile],
      },
    });

    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalledWith(validFile);
    });
  });

  it('prevents multiple file uploads in non-idle state', () => {
    render(<FileUploadZone {...defaultProps} state="uploading" />);

    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
    const file = createMockFile('test.csv', 1024, 'text/csv');

    // File input should be disabled during upload
    expect(fileInput).toBeDisabled();

    // Even if someone tries to manually trigger upload, it shouldn't work
    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(mockOnUpload).not.toHaveBeenCalled();
  });

  it('allows clicking in error state to retry', () => {
    render(
      <FileUploadZone
        {...defaultProps}
        state="error"
        error={{ message: "Upload failed", details: "Please try again" }}
      />
    );

    const uploadZone = screen.getByText(/upload failed/i).closest('.upload-zone') as HTMLElement;
    const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;

    // In error state, clicking should enable file selection again
    expect(fileInput).not.toBeDisabled();
    expect(uploadZone).toBeInTheDocument();
  });

  it('displays trust indicators', () => {
    render(<FileUploadZone {...defaultProps} />);

    expect(screen.getByText(/no signup required/i)).toBeInTheDocument();
    expect(screen.getByText(/files stay private/i)).toBeInTheDocument();
    expect(screen.getByText(/up to 100mb/i)).toBeInTheDocument();
    expect(screen.getByText(/auto-deleted in 24h/i)).toBeInTheDocument();
  });

  it('shows appropriate icons for different states', () => {
    const { rerender } = render(<FileUploadZone {...defaultProps} />);

    // Idle state - should show file text icon
    expect(document.querySelector('.lucide-file-text')).toBeInTheDocument();

    // Uploading state - should show upload icon with animation
    rerender(<FileUploadZone {...defaultProps} state="uploading" />);
    expect(document.querySelector('.lucide-upload')).toBeInTheDocument();

    // Success state - should show checkmark
    rerender(<FileUploadZone {...defaultProps} state="success" />);
    expect(document.querySelector('.lucide-check-circle')).toBeInTheDocument();

    // Error state - should show error icon
    rerender(<FileUploadZone {...defaultProps} state="error" />);
    expect(document.querySelector('.lucide-alert-circle')).toBeInTheDocument();
  });
});
