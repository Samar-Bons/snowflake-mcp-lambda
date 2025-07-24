// ABOUTME: Sidebar component showing uploaded files and database schema information
// ABOUTME: Provides file management, column details, and navigation between datasets

import { useState } from 'react';
import {
  FileText,
  Database,
  Settings,
  Upload,
  Trash2,
  X,
  ChevronDown,
  ChevronRight,
  Hash,
  Type,
  Calendar,
  CheckSquare
} from 'lucide-react';
import { Button } from '../ui/Button';
import { UploadedFile, TableSchema } from '../../types';

interface SchemaSidebarProps {
  files: UploadedFile[];
  activeFileId?: string;
  schema: TableSchema | null;
  onFileSelect: (fileId: string) => void;
  onDeleteFile: (fileId: string) => void;
  onNewUpload: () => void;
  onOpenSettings: () => void;
  isMobile: boolean;
  onClose?: () => void;
}

export function SchemaSidebar({
  files,
  activeFileId,
  schema,
  onFileSelect,
  onDeleteFile,
  onNewUpload,
  onOpenSettings,
  isMobile,
  onClose
}: SchemaSidebarProps) {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(
    new Set(['files', 'schema'])
  );

  const toggleSection = (section: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(section)) {
        newSet.delete(section);
      } else {
        newSet.add(section);
      }
      return newSet;
    });
  };

  const getColumnIcon = (type: string) => {
    switch (type) {
      case 'INTEGER':
      case 'DECIMAL':
        return Hash;
      case 'DATE':
      case 'DATETIME':
        return Calendar;
      case 'BOOLEAN':
        return CheckSquare;
      default:
        return Type;
    }
  };

  const formatFileSize = (bytes: number): string => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };

  const getStatusColor = (status: UploadedFile['processingStatus']) => {
    switch (status) {
      case 'completed':
        return 'text-success';
      case 'processing':
        return 'text-warning';
      case 'error':
        return 'text-error';
      default:
        return 'text-light-muted';
    }
  };

  const getStatusText = (status: UploadedFile['processingStatus']) => {
    switch (status) {
      case 'completed':
        return 'Ready';
      case 'processing':
        return 'Processing...';
      case 'error':
        return 'Error';
      default:
        return 'Uploading...';
    }
  };

  return (
    <div className="h-full bg-secondary border-r border-surface flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-surface flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Database className="h-5 w-5 text-blue-primary" />
          <span className="font-medium text-light-primary">Data Explorer</span>
        </div>

        {isMobile && onClose && (
          <Button
            variant="ghost"
            size="small"
            onClick={onClose}
            className="p-1"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto">
        {/* Files Section */}
        <div className="p-4">
          <button
            onClick={() => toggleSection('files')}
            className="flex items-center justify-between w-full text-left group"
          >
            <div className="flex items-center gap-2">
              {expandedSections.has('files') ? (
                <ChevronDown className="h-4 w-4 text-light-muted" />
              ) : (
                <ChevronRight className="h-4 w-4 text-light-muted" />
              )}
              <span className="text-sm font-medium text-light-primary">
                Files ({files.length})
              </span>
            </div>
          </button>

          {expandedSections.has('files') && (
            <div className="mt-3 space-y-2">
              {files.map((file) => (
                <div
                  key={file.id}
                  className={`
                    group p-3 rounded-lg border cursor-pointer transition-all
                    ${activeFileId === file.id
                      ? 'border-blue-primary bg-blue-primary/10'
                      : 'border-surface hover:border-surface-elevated hover:bg-surface/50'
                    }
                  `}
                  onClick={() => onFileSelect(file.id)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-2 flex-1 min-w-0">
                      <FileText className="h-4 w-4 text-blue-primary mt-0.5 flex-shrink-0" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-light-primary truncate">
                          {file.name}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`text-xs ${getStatusColor(file.processingStatus)}`}>
                            {getStatusText(file.processingStatus)}
                          </span>
                          {file.processingStatus === 'completed' && file.rowCount && (
                            <>
                              <span className="text-xs text-light-subtle">•</span>
                              <span className="text-xs text-light-muted">
                                {file.rowCount.toLocaleString()} rows
                              </span>
                            </>
                          )}
                        </div>
                        <p className="text-xs text-light-subtle mt-1">
                          {formatFileSize(file.size)} • {new Date(file.uploadedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>

                    <Button
                      variant="ghost"
                      size="small"
                      onClick={() => onDeleteFile(file.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 ml-2"
                    >
                      <Trash2 className="h-3 w-3 text-error" />
                    </Button>
                  </div>

                  {file.errorMessage && (
                    <div className="mt-2 p-2 bg-error/10 border border-error/20 rounded text-xs text-error">
                      {file.errorMessage}
                    </div>
                  )}
                </div>
              ))}

              <Button
                variant="outline"
                size="small"
                onClick={onNewUpload}
                className="w-full flex items-center gap-2 mt-3"
              >
                <Upload className="h-4 w-4" />
                Upload New File
              </Button>
            </div>
          )}
        </div>

        {/* Schema Section */}
        {schema && activeFileId && (
          <div className="p-4 border-t border-surface">
            <button
              onClick={() => toggleSection('schema')}
              className="flex items-center justify-between w-full text-left group"
            >
              <div className="flex items-center gap-2">
                {expandedSections.has('schema') ? (
                  <ChevronDown className="h-4 w-4 text-light-muted" />
                ) : (
                  <ChevronRight className="h-4 w-4 text-light-muted" />
                )}
                <span className="text-sm font-medium text-light-primary">
                  Schema ({schema.columns.length} columns)
                </span>
              </div>
            </button>

            {expandedSections.has('schema') && (
              <div className="mt-3 space-y-2">
                <div className="text-xs text-light-muted mb-3">
                  {schema.rowCount.toLocaleString()} rows in {schema.tableName}
                </div>

                {schema.columns.map((column, index) => {
                  const IconComponent = getColumnIcon(column.type);
                  return (
                    <div
                      key={index}
                      className="p-2 rounded border border-surface hover:border-surface-elevated hover:bg-surface/30 transition-all"
                    >
                      <div className="flex items-center gap-2">
                        <IconComponent className="h-3 w-3 text-blue-primary flex-shrink-0" />
                        <span className="text-xs font-medium text-light-primary truncate">
                          {column.name}
                        </span>
                        <span className="text-xs text-light-subtle ml-auto">
                          {column.type}
                        </span>
                      </div>

                      {column.sampleValues.length > 0 && (
                        <div className="mt-1 text-xs text-light-muted">
                          <span className="text-light-subtle">Examples: </span>
                          {column.sampleValues.slice(0, 3).join(', ')}
                          {column.sampleValues.length > 3 && '...'}
                        </div>
                      )}

                      {column.nullable && (
                        <div className="mt-1">
                          <span className="text-xs text-warning bg-warning/10 px-1 rounded">
                            nullable
                          </span>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-surface">
        <Button
          variant="ghost"
          size="small"
          onClick={onOpenSettings}
          className="w-full flex items-center gap-2 justify-start"
        >
          <Settings className="h-4 w-4" />
          Settings
        </Button>
      </div>
    </div>
  );
}
