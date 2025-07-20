// ABOUTME: Text input component for chat prompts with send functionality
// ABOUTME: Handles user input, loading states, and autorun toggle settings

import { useState, type KeyboardEvent } from 'react';
import { cn } from '../../utils/cn';

interface PromptInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  autorun: boolean;
  onAutorunChange: (autorun: boolean) => void;
  disabled?: boolean;
}

export function PromptInput({
  onSendMessage,
  isLoading,
  autorun,
  onAutorunChange,
  disabled = false
}: PromptInputProps) {
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    const trimmed = inputValue.trim();
    if (trimmed && !isLoading && !disabled) {
      onSendMessage(trimmed);
      setInputValue('');
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
      {/* Autorun toggle */}
      <div className="mb-3">
        <label className="flex items-center text-sm text-slate-600 dark:text-slate-400 cursor-pointer">
          <input
            type="checkbox"
            checked={autorun}
            onChange={(e) => onAutorunChange(e.target.checked)}
            disabled={disabled}
            className="mr-2 rounded border-slate-300 dark:border-slate-600 text-blue-600 focus:ring-blue-500 focus:ring-2"
          />
          Auto-run queries (skip confirmation)
        </label>
      </div>

      {/* Input area */}
      <div className="flex space-x-3">
        <div className="flex-1 relative">
          <textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about your data..."
            disabled={isLoading || disabled}
            rows={1}
            className={cn(
              'w-full resize-none rounded-lg border border-slate-300 dark:border-slate-600',
              'bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100',
              'px-4 py-3 text-sm placeholder-slate-500 dark:placeholder-slate-400',
              'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'min-h-[44px] max-h-32'
            )}
            style={{
              height: 'auto',
              minHeight: '44px'
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = 'auto';
              target.style.height = Math.min(target.scrollHeight, 128) + 'px';
            }}
          />
        </div>

        <button
          onClick={handleSend}
          disabled={!inputValue.trim() || isLoading || disabled}
          className={cn(
            'px-6 py-3 rounded-lg font-medium text-sm transition-colors',
            'bg-blue-600 hover:bg-blue-700 text-white',
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-blue-600',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2',
            'min-w-[80px] flex items-center justify-center'
          )}
        >
          {isLoading ? (
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Sending...</span>
            </div>
          ) : (
            'Send'
          )}
        </button>
      </div>

      {/* Hint text */}
      <div className="mt-2 text-xs text-slate-500 dark:text-slate-400">
        Press Enter to send, Shift+Enter for new line
      </div>
    </div>
  );
}
