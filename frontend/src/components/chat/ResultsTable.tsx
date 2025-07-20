// ABOUTME: Results table component for displaying query results with pagination
// ABOUTME: Shows tabular data with column headers and basic pagination controls

import { useState } from 'react';
import type { QueryResults } from '../../types/chat';
import { cn } from '../../utils/cn';

interface ResultsTableProps {
  results: QueryResults;
}

const ROWS_PER_PAGE = 10;

export function ResultsTable({ results }: ResultsTableProps) {
  const [currentPage, setCurrentPage] = useState(0);

  const totalPages = Math.ceil(results.rows.length / ROWS_PER_PAGE);
  const startIndex = currentPage * ROWS_PER_PAGE;
  const endIndex = startIndex + ROWS_PER_PAGE;
  const currentRows = results.rows.slice(startIndex, endIndex);

  if (!results.columns || results.columns.length === 0) {
    return (
      <div className="text-sm text-slate-500 dark:text-slate-400 italic">
        No data to display
      </div>
    );
  }

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded">
      {/* Results info */}
      <div className="px-4 py-2 bg-slate-50 dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center justify-between text-sm">
          <span className="text-slate-600 dark:text-slate-400">
            {results.rowCount} row{results.rowCount !== 1 ? 's' : ''}
            {results.truncated && ' (truncated)'}
          </span>
          {results.executionTimeMs && (
            <span className="text-slate-500 dark:text-slate-500">
              {results.executionTimeMs}ms
            </span>
          )}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          {/* Headers */}
          <thead className="bg-slate-50 dark:bg-slate-800">
            <tr>
              {results.columns.map((column, index) => (
                <th
                  key={index}
                  className="px-4 py-2 text-left text-slate-700 dark:text-slate-300 font-medium border-b border-slate-200 dark:border-slate-700"
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          {/* Body */}
          <tbody>
            {currentRows.map((row, rowIndex) => (
              <tr
                key={rowIndex}
                className={cn(
                  'border-b border-slate-100 dark:border-slate-800',
                  rowIndex % 2 === 0 ? 'bg-white dark:bg-slate-900' : 'bg-slate-25 dark:bg-slate-950'
                )}
              >
                {row.map((cell, cellIndex) => (
                  <td
                    key={cellIndex}
                    className="px-4 py-2 text-slate-900 dark:text-slate-100"
                  >
                    {cell === null || cell === undefined ? (
                      <span className="text-slate-400 italic">null</span>
                    ) : (
                      String(cell)
                    )}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="px-4 py-3 bg-slate-50 dark:bg-slate-800 border-t border-slate-200 dark:border-slate-700">
          <div className="flex items-center justify-between">
            <div className="text-sm text-slate-600 dark:text-slate-400">
              Page {currentPage + 1} of {totalPages}
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage(Math.max(0, currentPage - 1))}
                disabled={currentPage === 0}
                className="px-3 py-1 text-sm bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-600"
              >
                Previous
              </button>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages - 1, currentPage + 1))}
                disabled={currentPage === totalPages - 1}
                className="px-3 py-1 text-sm bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-50 dark:hover:bg-slate-600"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
