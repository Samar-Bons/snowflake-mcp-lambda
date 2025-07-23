// ABOUTME: Main chat interface component with message display and input handling
// ABOUTME: Handles user messages, SQL generation, query confirmation, and results display

import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';
import { ChatMessage } from '../chat/ChatMessage';
import { DataResults } from '../data/DataResults';
import { chatService } from '../../services/chat';
import { ChatMessage as ChatMessageType, TableSchema, AppSettings } from '../../types';

interface ChatWindowProps {
  messages: ChatMessageType[];
  isTyping: boolean;
  onSendMessage: (message: string) => void;
  onExecuteQuery: (messageId: string, sqlQuery: string) => void;
  schema: TableSchema;
  settings: AppSettings;
}

export function ChatWindow({
  messages,
  isTyping,
  onSendMessage,
  onExecuteQuery,
  schema,
  settings
}: ChatWindowProps) {
  const [inputValue, setInputValue] = useState('');
  const [suggestions] = useState(() => chatService.getSampleQueries(schema));
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [inputValue]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
    textareaRef.current?.focus();
  };

  const renderWelcomeMessage = () => (
    <div className="text-center py-12 space-y-6">
      <div className="w-16 h-16 bg-purple-primary/20 rounded-full flex items-center justify-center mx-auto">
        <Sparkles className="h-8 w-8 text-purple-primary" />
      </div>
      
      <div className="space-y-2">
        <h3 className="text-xl font-medium text-light-primary">
          Ready to explore your data!
        </h3>
        <p className="text-light-muted max-w-md mx-auto">
          I can help you analyze your CSV data. Try asking questions in plain English about your {schema.rowCount.toLocaleString()} rows of data.
        </p>
      </div>

      <div className="space-y-3">
        <p className="text-sm font-medium text-light-primary">Try these examples:</p>
        <div className="flex flex-wrap gap-2 justify-center max-w-2xl mx-auto">
          {suggestions.slice(0, 4).map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion)}
              className="px-3 py-2 text-xs bg-surface hover:bg-surface-elevated text-light-secondary hover:text-light-primary rounded-lg transition-all border border-surface-elevated hover:border-blue-primary/50"
            >
              "{suggestion}"
            </button>
          ))}
        </div>
      </div>

      <div className="text-xs text-light-subtle space-y-1">
        <p>Available columns: {schema.columns.map(col => col.name).join(', ')}</p>
        <p>Query limit: {settings.rowLimit} rows • Auto-run: {settings.autoRunQueries ? 'On' : 'Off'}</p>
      </div>
    </div>
  );

  return (
    <div className="h-full flex flex-col">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
        {messages.length === 0 ? (
          renderWelcomeMessage()
        ) : (
          <>
            {messages.map((message) => (
              <div key={message.id}>
                <ChatMessage
                  message={message}
                  onExecuteQuery={onExecuteQuery}
                  settings={settings}
                />
                
                {/* Display query results if available */}
                {message.queryResults && (
                  <div className="mt-4">
                    <DataResults
                      result={message.queryResults}
                      onExport={(format) => {
                        if (message.queryResults) {
                          chatService.downloadResults(
                            message.queryResults.id,
                            `query-results-${Date.now()}`,
                            format
                          );
                        }
                      }}
                    />
                  </div>
                )}
              </div>
            ))}
            
            {isTyping && (
              <div className="flex items-start gap-3">
                <div className="chat-avatar chat-avatar--assistant">
                  AI
                </div>
                <div className="chat-message__content">
                  <div className="flex items-center gap-2 text-light-muted">
                    <span className="text-sm">Thinking...</span>
                    <div className="typing-dots">
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                      <div className="typing-dot"></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-surface bg-surface/50 p-4">
        <form onSubmit={handleSubmit} className="flex gap-3 items-end max-w-4xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything about your data..."
              className="form-textarea resize-none min-h-[44px] max-h-32 pr-12"
              rows={1}
              disabled={isTyping}
            />
            
            {/* Send Button */}
            <Button
              type="submit"
              variant="primary"
              size="small"
              disabled={!inputValue.trim() || isTyping}
              className="absolute right-2 bottom-2 p-2 min-w-0"
            >
              <Send className="h-4 w-4" />
              <span className="sr-only">Send message</span>
            </Button>
          </div>
        </form>

        {/* Quick suggestions for empty input */}
        {inputValue === '' && messages.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2 justify-center">
            {suggestions.slice(4, 8).map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="px-2 py-1 text-xs bg-surface-elevated hover:bg-blue-primary/20 text-light-muted hover:text-blue-primary rounded transition-all"
              >
                {suggestion}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}