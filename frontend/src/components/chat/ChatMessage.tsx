// ABOUTME: Individual chat message component with SQL display and execution controls
// ABOUTME: Handles user and assistant messages with syntax highlighting and action buttons

import React from 'react';
import { User, Bot, Play, Edit3, Copy, Check } from 'lucide-react';
import { Button } from '../ui/Button';
import { ChatMessage as ChatMessageType, AppSettings } from '../../types';

interface ChatMessageProps {
  message: ChatMessageType;
  onExecuteQuery: (messageId: string, sqlQuery: string) => void;
  settings: AppSettings;
}

export function ChatMessage({ message, onExecuteQuery, settings }: ChatMessageProps) {
  const [copied, setCopied] = React.useState(false);

  const handleCopySQL = async (sql: string) => {
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy SQL:', error);
    }
  };

  const handleExecuteQuery = () => {
    if (message.sqlQuery) {
      onExecuteQuery(message.id, message.sqlQuery);
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(timestamp);
  };

  const renderSQLBlock = (sql: string) => (
    <div className="bg-surface/80 border border-surface-elevated rounded-lg overflow-hidden mt-3">
      <div className="flex items-center justify-between px-3 py-2 bg-surface-elevated border-b border-surface">
        <span className="text-xs font-medium text-light-primary">Generated SQL</span>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="small"
            onClick={() => handleCopySQL(sql)}
            className="p-1"
          >
            {copied ? (
              <Check className="h-3 w-3 text-success" />
            ) : (
              <Copy className="h-3 w-3" />
            )}
          </Button>

          {!message.queryResults && (
            <>
              <Button
                size="small"
                onClick={handleExecuteQuery}
                className="text-xs px-2 py-1 flex items-center gap-1"
              >
                <Play className="h-3 w-3" />
                Execute
              </Button>

              <Button
                variant="outline"
                size="small"
                className="text-xs px-2 py-1 flex items-center gap-1"
              >
                <Edit3 className="h-3 w-3" />
                Edit
              </Button>
            </>
          )}
        </div>
      </div>

      <pre className="px-3 py-3 text-sm text-light-primary font-mono overflow-x-auto">
        <code>{sql}</code>
      </pre>
    </div>
  );

  return (
    <div className={`chat-message ${message.type === 'user' ? 'chat-message--user' : 'chat-message--assistant'}`}>
      {/* Avatar */}
      <div className={`chat-avatar ${message.type === 'assistant' ? 'chat-avatar--assistant' : ''}`}>
        {message.type === 'user' ? (
          <User className="h-4 w-4" />
        ) : (
          <Bot className="h-4 w-4" />
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        <div className="chat-message__content">
          {/* Text content */}
          {typeof message.content === 'string' ? (
            <div className="whitespace-pre-wrap break-words">
              {message.content}
            </div>
          ) : (
            message.content
          )}

          {/* SQL Query Display */}
          {message.sqlQuery && renderSQLBlock(message.sqlQuery)}

          {/* Query execution status */}
          {message.queryResults?.status === 'error' && (
            <div className="mt-3 p-3 bg-error/10 border border-error/20 rounded-lg">
              <div className="flex items-center gap-2 text-error text-sm">
                <span className="font-medium">Query Error:</span>
                <span>{message.queryResults.errorMessage}</span>
              </div>
            </div>
          )}
        </div>

        {/* Message metadata */}
        <div className="flex items-center justify-between mt-2 text-xs text-light-subtle">
          <span>{formatTimestamp(message.timestamp)}</span>

          {message.status === 'sending' && (
            <span className="flex items-center gap-1">
              <div className="w-1 h-1 bg-blue-primary rounded-full animate-pulse" />
              Sending...
            </span>
          )}

          {message.status === 'error' && (
            <span className="text-error">Failed to send</span>
          )}

          {message.queryResults && message.queryResults.status === 'success' && (
            <span className="text-success">
              {message.queryResults.data.length} rows • {message.queryResults.executionTime}ms
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
