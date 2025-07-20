// ABOUTME: Modal component for SQL confirmation before execution
// ABOUTME: Shows generated SQL with options to confirm, edit, or cancel execution

import { useState, useEffect } from 'react';
import { cn } from '../../utils/cn';

interface SQLConfirmationModalProps {
  isOpen: boolean;
  sql: string;
  onConfirm: () => void;
  onCancel: () => void;
  onEdit?: (newSql: string) => void;
  isExecuting?: boolean;
}

export function SQLConfirmationModal({
  isOpen,
  sql,
  onConfirm,
  onCancel,
  onEdit,
  isExecuting = false
}: SQLConfirmationModalProps) {
  const [editMode, setEditMode] = useState(false);
  const [editedSql, setEditedSql] = useState(sql);

  // Synchronize editedSql with sql prop when it changes
  useEffect(() => {
    setEditedSql(sql);
  }, [sql]);

  if (!isOpen) return null;

  const handleEdit = () => {
    if (editMode && onEdit) {
      onEdit(editedSql);
      setEditMode(false);
    } else {
      setEditedSql(sql);
      setEditMode(true);
    }
  };

  const handleCancel = () => {
    setEditMode(false);
    setEditedSql(sql);
    onCancel();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white dark:bg-slate-800 rounded-lg max-w-4xl w-full max-h-[80vh] flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">
            Confirm SQL Execution
          </h3>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
            Review the generated SQL query before executing
          </p>
        </div>

        {/* SQL Content */}
        <div className="flex-1 p-6 overflow-auto">
          <div className="mb-4">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
              Generated SQL Query:
            </label>
            {editMode ? (
              <textarea
                value={editedSql}
                onChange={(e) => setEditedSql(e.target.value)}
                className={cn(
                  'w-full h-64 p-4 border border-slate-300 dark:border-slate-600 rounded-lg',
                  'bg-slate-50 dark:bg-slate-900 text-slate-900 dark:text-slate-100',
                  'font-mono text-sm leading-relaxed',
                  'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                  'resize-none'
                )}
                spellCheck={false}
              />
            ) : (
              <div className="bg-slate-900 dark:bg-slate-950 rounded-lg p-4 border">
                <pre className="text-green-400 font-mono text-sm leading-relaxed whitespace-pre-wrap break-words">
                  {sql}
                </pre>
              </div>
            )}
          </div>

          {/* Warning */}
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                  Read-only execution
                </h4>
                <div className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  This query will be executed in read-only mode with a 500-row limit for safety.
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-slate-200 dark:border-slate-700 flex justify-between">
          <div className="flex space-x-3">
            {onEdit && (
              <button
                onClick={handleEdit}
                disabled={isExecuting}
                className={cn(
                  'px-4 py-2 text-sm font-medium rounded-lg border transition-colors',
                  'border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300',
                  'hover:bg-slate-50 dark:hover:bg-slate-700',
                  'disabled:opacity-50 disabled:cursor-not-allowed'
                )}
              >
                {editMode ? 'Save Changes' : 'Edit SQL'}
              </button>
            )}
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleCancel}
              disabled={isExecuting}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-lg border transition-colors',
                'border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300',
                'hover:bg-slate-50 dark:hover:bg-slate-700',
                'disabled:opacity-50 disabled:cursor-not-allowed'
              )}
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              disabled={isExecuting}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-lg transition-colors',
                'bg-blue-600 hover:bg-blue-700 text-white',
                'disabled:opacity-50 disabled:cursor-not-allowed',
                'min-w-[100px] flex items-center justify-center'
              )}
            >
              {isExecuting ? (
                <div className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                  <span>Executing...</span>
                </div>
              ) : (
                'Execute Query'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
