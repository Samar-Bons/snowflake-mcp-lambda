// ABOUTME: Schema preview component showing detected columns and sample data
// ABOUTME: Displays CSV structure with confirmation options to proceed to chat

// Remove React import as it's not needed
import {
  Database,
  FileSpreadsheet,
  CheckCircle,
  ArrowRight,
  Upload,
  Download,
  Eye
} from 'lucide-react';
import { Button } from '../ui/Button';
import { Card } from '../ui/Card';
import { TableSchema, UploadedFile } from '../../types';

interface SchemaPreviewProps {
  file: UploadedFile;
  schema: TableSchema;
  sampleData: Array<Record<string, any>>;
  onStartChat: () => void;
  onUploadDifferent: () => void;
}

export function SchemaPreview({
  file,
  schema,
  sampleData,
  onStartChat,
  onUploadDifferent
}: SchemaPreviewProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  const formatSampleValue = (value: any, type: string): string => {
    if (value === null || value === undefined) return 'null';

    switch (type) {
      case 'INTEGER':
      case 'DECIMAL':
        return typeof value === 'number' ? value.toLocaleString() : String(value);
      case 'DATE':
      case 'DATETIME':
        try {
          const date = value instanceof Date ? value : new Date(value);
          return isNaN(date.getTime()) ? String(value) : date.toLocaleDateString();
        } catch {
          return String(value);
        }
      case 'BOOLEAN':
        return value ? 'true' : 'false';
      default:
        const str = String(value);
        return str.length > 20 ? str.substring(0, 20) + '...' : str;
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'INTEGER':
      case 'DECIMAL':
        return '🔢';
      case 'DATE':
      case 'DATETIME':
        return '📅';
      case 'BOOLEAN':
        return '✓';
      default:
        return '📝';
    }
  };

  return (
    <div className="min-h-screen bg-secondary-dark flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <div className="relative">
              <FileSpreadsheet className="h-16 w-16 text-blue-primary" />
              <div className="absolute -top-2 -right-2 bg-success rounded-full p-1">
                <CheckCircle className="h-4 w-4 text-white" />
              </div>
            </div>
          </div>

          <h1 className="text-3xl font-bold text-light-primary mb-2">
            Your Data is Ready!
          </h1>
          <p className="text-light-muted mb-4">
            We've analyzed <span className="font-medium text-light-primary">{file.name}</span> and detected the following structure
          </p>

          {/* File Stats */}
          <div className="inline-flex items-center gap-6 text-sm text-light-secondary bg-surface/30 rounded-lg px-4 py-2">
            <div className="flex items-center gap-1">
              <Database className="h-4 w-4" />
              <span>{schema.rowCount.toLocaleString()} rows</span>
            </div>
            <div className="flex items-center gap-1">
              <Eye className="h-4 w-4" />
              <span>{schema.columns.length} columns</span>
            </div>
            <div className="flex items-center gap-1">
              <Download className="h-4 w-4" />
              <span>{formatFileSize(file.size)}</span>
            </div>
          </div>
        </div>

        {/* Schema Table */}
        <Card className="mb-8">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-light-primary mb-4 flex items-center gap-2">
              <Database className="h-5 w-5 text-blue-primary" />
              Data Structure
            </h3>

            <div className="overflow-hidden rounded-lg border border-surface">
              <div className="overflow-x-auto">
                <table className="schema-table w-full">
                  <thead>
                    <tr className="bg-surface-elevated">
                      <th className="px-4 py-3 text-left text-sm font-medium text-light-primary">
                        Column Name
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-light-primary">
                        Type
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-light-primary">
                        Sample Data
                      </th>
                      <th className="px-4 py-3 text-left text-sm font-medium text-light-primary">
                        Nullable
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {schema.columns.map((column) => {
                      // Get sample values for this column
                      const sampleValues = column.sampleValues || [];

                      return (
                        <tr
                          key={column.name}
                          className="border-b border-surface/50 hover:bg-surface/30 transition-colors"
                        >
                          <td className="px-4 py-3">
                            <div className="flex items-center gap-2">
                              <span className="text-lg">{getTypeIcon(column.type)}</span>
                              <span className="font-medium text-light-primary">
                                {column.name}
                              </span>
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-primary/20 text-blue-primary">
                              {column.type.toUpperCase()}
                            </span>
                          </td>
                          <td className="px-4 py-3">
                            <div className="text-sm text-light-secondary font-mono">
                              {sampleValues.length > 0 ? (
                                sampleValues
                                  .map(val => formatSampleValue(val, column.type))
                                  .join(', ')
                              ) : (
                                <span className="text-light-subtle italic">No data</span>
                              )}
                            </div>
                          </td>
                          <td className="px-4 py-3">
                            <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
                              column.nullable
                                ? 'bg-warning/20 text-warning'
                                : 'bg-success/20 text-success'
                            }`}>
                              {column.nullable ? 'Yes' : 'No'}
                            </span>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Card>

        {/* Sample Data Preview */}
        <Card className="mb-8">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-light-primary mb-4 flex items-center gap-2">
              <Eye className="h-5 w-5 text-purple-primary" />
              Sample Data Preview
              <span className="text-sm text-light-muted font-normal ml-2">
                (First {Math.min(sampleData.length, 5)} rows)
              </span>
            </h3>

            <div className="overflow-hidden rounded-lg border border-surface">
              <div className="overflow-x-auto">
                <table className="data-table w-full">
                  <thead>
                    <tr className="bg-surface-elevated">
                      {schema.columns.map((column) => (
                        <th
                          key={column.name}
                          className="px-4 py-3 text-left text-sm font-medium text-light-primary whitespace-nowrap"
                        >
                          {column.name}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {sampleData.slice(0, 5).map((row, rowIndex) => (
                      <tr
                        key={rowIndex}
                        className="border-b border-surface/50 hover:bg-surface/30 transition-colors"
                      >
                        {schema.columns.map((column) => (
                          <td
                            key={column.name}
                            className="px-4 py-3 text-sm text-light-secondary"
                          >
                            <div className={`${(column.type === 'INTEGER' || column.type === 'DECIMAL') ? 'text-right font-mono' : ''}`}>
                              {formatSampleValue(row[column.name], column.type)}
                            </div>
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </Card>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button
            variant="outline"
            onClick={onUploadDifferent}
            className="flex items-center gap-2"
          >
            <Upload className="h-4 w-4" />
            Upload Different File
          </Button>

          <Button
            variant="primary"
            size="large"
            onClick={onStartChat}
            className="flex items-center gap-2"
          >
            Start Chatting with Your Data
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>

        {/* Data Quality Indicators */}
        <div className="mt-8 p-4 bg-surface/30 rounded-lg">
          <h4 className="text-sm font-medium text-light-primary mb-3">Data Quality Summary</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-success" />
              <span className="text-light-secondary">
                All columns have clear names
              </span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-success" />
              <span className="text-light-secondary">
                Data types detected successfully
              </span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-success" />
              <span className="text-light-secondary">
                Ready for natural language queries
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
