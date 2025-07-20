// ABOUTME: Main chat window component that orchestrates the entire chat experience
// ABOUTME: Manages chat state, message flow, backend integration, and component coordination

import { useState, useRef, useEffect } from 'react';
import type { ChatMessage, ChatState } from '../../types/chat';
import { ChatService } from '../../services/chat';
import { MessageBubble } from './MessageBubble';
import { PromptInput } from './PromptInput';
import { SQLConfirmationModal } from './SQLConfirmationModal';
import { getErrorMessage } from '../../types/api';

export function ChatWindow() {
  const [chatState, setChatState] = useState<ChatState>({
    messages: [],
    isLoading: false,
    error: null,
    autorun: false,
    showSqlModal: false
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatState.messages]);

  // Add a message to the chat
  const addMessage = (message: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    const newMessage: ChatMessage = {
      ...message,
      id: crypto.randomUUID(),
      timestamp: new Date()
    };

    setChatState(prev => ({
      ...prev,
      messages: [...prev.messages, newMessage]
    }));
  };

  // Handle sending a user message
  const handleSendMessage = async (prompt: string) => {
    // Add user message
    addMessage({
      type: 'user',
      content: prompt
    });

    setChatState(prev => ({ ...prev, isLoading: true, error: null }));

    try {
      const response = await ChatService.sendMessage({
        prompt,
        autorun: chatState.autorun
      });

      if (chatState.autorun && response.rows) {
        // Auto-run enabled and we got results - add assistant message with results
        addMessage({
          type: 'assistant',
          content: 'Query executed successfully',
          sql: response.sql,
          results: {
            columns: response.columns || [],
            rows: response.rows,
            rowCount: response.rowCount || 0,
            truncated: response.truncated || false,
            executionTimeMs: response.executionTimeMs
          }
        });
      } else {
        // Show SQL confirmation modal
        setChatState(prev => ({
          ...prev,
          pendingSql: response.sql,
          showSqlModal: true
        }));
      }
    } catch (error) {
      addMessage({
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request.',
        error: getErrorMessage(error)
      });
    } finally {
      setChatState(prev => ({ ...prev, isLoading: false }));
    }
  };

  // Handle SQL confirmation
  const handleConfirmSQL = async () => {
    if (!chatState.pendingSql) return;

    setChatState(prev => ({ ...prev, showSqlModal: false, isLoading: true }));

    try {
      const response = await ChatService.executeSQL(chatState.pendingSql);

      addMessage({
        type: 'assistant',
        content: 'Query executed successfully',
        sql: chatState.pendingSql,
        results: {
          columns: response.columns || [],
          rows: response.rows || [],
          rowCount: response.rowCount || 0,
          truncated: response.truncated || false,
          executionTimeMs: response.executionTimeMs
        }
      });
    } catch (error) {
      addMessage({
        type: 'assistant',
        content: 'Failed to execute the query.',
        sql: chatState.pendingSql,
        error: getErrorMessage(error)
      });
    } finally {
      setChatState(prev => ({
        ...prev,
        isLoading: false,
        pendingSql: undefined
      }));
    }
  };

  // Handle SQL cancellation
  const handleCancelSQL = () => {
    // Capture the current pendingSql before clearing it to avoid stale state
    const currentPendingSql = chatState.pendingSql;

    setChatState(prev => ({
      ...prev,
      showSqlModal: false,
      pendingSql: undefined
    }));

    addMessage({
      type: 'assistant',
      content: 'Query execution cancelled.',
      sql: currentPendingSql
    });
  };

  // Handle SQL editing
  const handleEditSQL = async (newSql: string) => {
    setChatState(prev => ({ ...prev, pendingSql: newSql }));
  };

  // Handle autorun toggle
  const handleAutorunChange = (autorun: boolean) => {
    setChatState(prev => ({ ...prev, autorun }));
  };

  // Initial welcome message
  useEffect(() => {
    if (chatState.messages.length === 0) {
      addMessage({
        type: 'system',
        content: 'Welcome to Snowflake Chat! Ask me anything about your data and I\'ll help you write SQL queries.'
      });
    }
  }, []);

  return (
    <div className="flex flex-col h-full bg-slate-50 dark:bg-slate-900">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="max-w-4xl mx-auto">
          {chatState.messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {/* Loading indicator */}
          {chatState.isLoading && (
            <div className="flex justify-start mb-4">
              <div className="bg-slate-100 dark:bg-slate-800 rounded-lg px-4 py-3">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                  <span className="text-sm text-slate-600 dark:text-slate-400">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input area */}
      <div className="flex-shrink-0">
        <div className="max-w-4xl mx-auto">
          <PromptInput
            onSendMessage={handleSendMessage}
            isLoading={chatState.isLoading}
            autorun={chatState.autorun}
            onAutorunChange={handleAutorunChange}
          />
        </div>
      </div>

      {/* SQL Confirmation Modal */}
      <SQLConfirmationModal
        isOpen={chatState.showSqlModal}
        sql={chatState.pendingSql || ''}
        onConfirm={handleConfirmSQL}
        onCancel={handleCancelSQL}
        onEdit={handleEditSQL}
        isExecuting={chatState.isLoading}
      />
    </div>
  );
}
