// ABOUTME: Message bubble component for displaying chat messages
// ABOUTME: Handles user prompts, assistant responses, and error states with proper styling

import type { ChatMessage } from '../../types/chat';
import { cn } from '../../utils/cn';
import { ResultsTable } from './ResultsTable';

interface MessageBubbleProps {
  message: ChatMessage;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.type === 'user';
  const isSystem = message.type === 'system';

  return (
    <div className={cn(
      'flex w-full mb-4',
      isUser ? 'justify-end' : 'justify-start'
    )}>
      <div className={cn(
        'max-w-[80%] rounded-lg px-4 py-3',
        isUser ? 'bg-blue-600 text-white' : 'bg-slate-100 dark:bg-slate-800 text-slate-900 dark:text-slate-100',
        isSystem && 'bg-yellow-100 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200'
      )}>
        {/* Message content */}
        <div className="whitespace-pre-wrap text-sm leading-relaxed">
          {message.content}
        </div>

        {/* SQL display if present */}
        {message.sql && (
          <div className="mt-3 p-3 bg-slate-900 dark:bg-slate-950 rounded border">
            <div className="text-xs text-slate-400 mb-2 font-mono">Generated SQL:</div>
            <code className="text-sm text-green-400 font-mono break-all">
              {message.sql}
            </code>
          </div>
        )}

        {/* Results table if present */}
        {message.results && (
          <div className="mt-3">
            <ResultsTable results={message.results} />
          </div>
        )}

        {/* Error display */}
        {message.error && (
          <div className="mt-3 p-3 bg-red-100 dark:bg-red-900/20 rounded border border-red-200 dark:border-red-800">
            <div className="text-xs text-red-600 dark:text-red-400 mb-1 font-semibold">Error:</div>
            <div className="text-sm text-red-700 dark:text-red-300">
              {message.error}
            </div>
          </div>
        )}

        {/* Timestamp */}
        <div className={cn(
          'text-xs mt-2 opacity-70',
          isUser ? 'text-blue-100' : 'text-slate-500 dark:text-slate-400'
        )}>
          {message.timestamp.toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
}
