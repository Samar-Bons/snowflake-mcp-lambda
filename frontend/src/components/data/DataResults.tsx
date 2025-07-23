// ABOUTME: Data results table component with pagination, sorting, and export functionality
// ABOUTME: Displays query results in a formatted table with metadata and action buttons

import React, { useState } from 'react';
import { 
  Download, 
  Copy, 
  Check, 
  ChevronLeft, 
  ChevronRight, 
  ArrowUp, 
  ArrowDown,
  FileText,
  BarChart3
} from 'lucide-react';
import { Button } from '../ui/Button';
import { QueryResult } from '../../types';

interface DataResultsProps {
  result: QueryResult;
  onExport: (format: 'csv' | 'json') => void;
}

export function DataResults({ result, onExport }: DataResultsProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [copied, setCopied] = useState(false);
  const pageSize = 10; // Show 10 rows per page in results

  // Calculate pagination
  const totalPages = Math.ceil(result.data.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const currentData = result.data.slice(startIndex, endIndex);

  const handleSort = (columnKey: string) => {
    if (sortColumn === columnKey) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(columnKey);
      setSortDirection('asc');
    }
  };

  const handleCopyResults = async () => {
    try {
      const csvContent = [
        result.columns.map(col => col.label).join(','),
        ...result.data.map(row => 
          result.columns.map(col => {
            const value = row[col.key];
            // Escape quotes and wrap in quotes if contains comma
            const stringValue = String(value ?? '');
            return stringValue.includes(',') || stringValue.includes('"') 
              ? `"${stringValue.replace(/"/g, '""')}"` 
              : stringValue;
          }).join(',')
        )
      ].join('\n');

      await navigator.clipboard.writeText(csvContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy results:', error);
    }
  };

  const formatCellValue = (value: any, type: string) => {
    if (value === null || value === undefined) {
      return <span className="text-light-subtle italic">null</span>;
    }

    switch (type) {
      case 'number':
        return (
          <span className="text-right font-mono">
            {typeof value === 'number' ? value.toLocaleString() : value}
          </span>
        );
      case 'date':
        const date = value instanceof Date ? value : new Date(value);
        return (
          <span className="font-mono">
            {isNaN(date.getTime()) ? value : date.toLocaleDateString()}
          </span>
        );
      case 'boolean':
        return (
          <span className={`inline-flex items-center px-2 py-1 rounded text-xs font-medium ${
            value ? 'bg-success/20 text-success' : 'bg-error/20 text-error'
          }`}>
            {value ? 'True' : 'False'}
          </span>
        );
      default:
        return <span className="break-words">{String(value)}</span>;
    }
  };

  const getSortedData = () => {
    if (!sortColumn) return currentData;

    return [...currentData].sort((a, b) => {
      const aValue = a[sortColumn];
      const bValue = b[sortColumn];
      
      // Handle null/undefined values
      if (aValue === null || aValue === undefined) return sortDirection === 'asc' ? 1 : -1;
      if (bValue === null || bValue === undefined) return sortDirection === 'asc' ? -1 : 1;
      
      // Compare values
      const comparison = aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      return sortDirection === 'asc' ? comparison : -comparison;
    });
  };

  const sortedData = getSortedData();

  return (
    <div className="space-y-4">
      {/* Results Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-blue-primary" />
            <span className="font-medium text-light-primary">Query Results</span>
          </div>
          
          <div className="text-sm text-light-muted">
            Showing {Math.min(result.data.length, pageSize)} of {result.totalRows} rows
            {result.executionTime && (
              <> • Executed in {result.executionTime}ms</>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="small"
            onClick={handleCopyResults}
            className="flex items-center gap-2"
          >
            {copied ? (
              <Check className="h-4 w-4 text-success" />
            ) : (
              <Copy className="h-4 w-4" />
            )}
            Copy
          </Button>
          
          <Button
            variant="outline"
            size="small"
            onClick={() => onExport('csv')}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
          
          <Button
            variant="outline"
            size="small"
            onClick={() => onExport('json')}
            className="flex items-center gap-2"
          >
            <FileText className="h-4 w-4" />
            JSON
          </Button>
        </div>
      </div>

      {/* Results Table */}
      <div className="overflow-hidden rounded-lg border border-surface">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                {result.columns.map((column) => (
                  <th 
                    key={column.key}
                    className="cursor-pointer hover:bg-surface-elevated transition-colors"
                    onClick={() => handleSort(column.key)}
                  >
                    <div className="flex items-center gap-2">
                      <span>{column.label}</span>
                      {sortColumn === column.key ? (
                        sortDirection === 'asc' ? (
                          <ArrowUp className="h-3 w-3" />
                        ) : (
                          <ArrowDown className="h-3 w-3" />
                        )
                      ) : (
                        <div className="h-3 w-3" />
                      )}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {sortedData.map((row, rowIndex) => (
                <tr key={rowIndex} className="hover:bg-surface transition-colors">
                  {result.columns.map((column) => (
                    <td key={column.key} className={column.type === 'number' ? 'text-right' : ''}>
                      {formatCellValue(row[column.key], column.type)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Empty State */}
        {result.data.length === 0 && (
          <div className="p-12 text-center">
            <BarChart3 className="h-12 w-12 text-light-muted mx-auto mb-4" />
            <h3 className="text-lg font-medium text-light-primary mb-2">
              No Results Found
            </h3>
            <p className="text-light-muted">
              Your query didn't return any data. Try adjusting your search criteria.
            </p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-between">
          <div className="text-sm text-light-muted">
            Page {currentPage} of {totalPages}
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="small"
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="flex items-center gap-1"
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </Button>
            
            <div className="flex items-center gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                let pageNum;
                if (totalPages <= 5) {
                  pageNum = i + 1;
                } else if (currentPage <= 3) {
                  pageNum = i + 1;
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i;
                } else {
                  pageNum = currentPage - 2 + i;
                }

                return (
                  <Button
                    key={pageNum}
                    variant={currentPage === pageNum ? "primary" : "ghost"}
                    size="small"
                    onClick={() => setCurrentPage(pageNum)}
                    className="w-8 h-8 p-0"
                  >
                    {pageNum}
                  </Button>
                );
              })}
            </div>
            
            <Button
              variant="outline"
              size="small"
              onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
              disabled={currentPage === totalPages}
              className="flex items-center gap-1"
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}

      {/* Result Summary */}
      <div className="text-xs text-light-subtle p-3 bg-surface/30 rounded-lg">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <span className="font-medium">Total Rows:</span> {result.totalRows.toLocaleString()}
          </div>
          <div>
            <span className="font-medium">Columns:</span> {result.columns.length}
          </div>
          <div>
            <span className="font-medium">Execution Time:</span> {result.executionTime}ms
          </div>
          <div>
            <span className="font-medium">Status:</span> 
            <span className={`ml-1 ${result.status === 'success' ? 'text-success' : 'text-error'}`}>
              {result.status}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}