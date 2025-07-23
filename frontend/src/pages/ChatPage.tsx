// ABOUTME: Main chat interface page with desktop sidebar and mobile responsive layout
// ABOUTME: Handles chat conversations, file management, and query results display

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Menu, X, Upload, Settings, FileText, MessageSquare } from 'lucide-react';
import { ThemeToggle } from '../components/ui/ThemeToggle';
import { Button } from '../components/ui/Button';
import { ChatWindow } from '../components/chat/ChatWindow';
import { SchemaSidebar } from '../components/schema/SchemaSidebar';
import { FileUploadZone } from '../components/upload/FileUploadZone';
import { Modal } from '../components/ui/Modal';
import { fileUploadService } from '../services/fileUpload';
import { chatService } from '../services/chat';
import { 
  UploadedFile, 
  TableSchema, 
  ChatMessage, 
  AppSettings, 
  UploadProgress, 
  FileUploadError 
} from '../types';

interface ChatPageProps {
  theme: 'dark' | 'light';
  onToggleTheme: () => void;
}

export function ChatPage({ theme, onToggleTheme }: ChatPageProps) {
  const { fileId } = useParams<{ fileId?: string }>();
  const navigate = useNavigate();
  
  // State management
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [uploadModalOpen, setUploadModalOpen] = useState(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  
  // Data state
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [activeFile, setActiveFile] = useState<UploadedFile | null>(null);
  const [schema, setSchema] = useState<TableSchema | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  
  // Upload state
  const [uploadState, setUploadState] = useState<'idle' | 'uploading' | 'processing' | 'success' | 'error'>('idle');
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>();
  const [uploadError, setUploadError] = useState<FileUploadError>();
  
  // Settings
  const [settings, setSettings] = useState<AppSettings>({
    rowLimit: 500,
    autoRunQueries: false,
    exportFormat: 'csv',
    theme: theme,
  });

  // Mobile detection
  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) {
        setSidebarOpen(false);
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Load initial data
  useEffect(() => {
    loadFiles();
  }, []);

  // Load specific file data when fileId changes
  useEffect(() => {
    if (fileId) {
      loadFileData(fileId);
    }
  }, [fileId]);

  const loadFiles = async () => {
    try {
      const uploadedFiles = await fileUploadService.getUploadedFiles();
      setFiles(uploadedFiles);
      
      // If no fileId in URL but files exist, redirect to first file
      if (!fileId && uploadedFiles.length > 0) {
        navigate(`/chat/${uploadedFiles[0].id}`, { replace: true });
      }
    } catch (error) {
      console.error('Failed to load files:', error);
    }
  };

  const loadFileData = async (selectedFileId: string) => {
    try {
      const file = files.find(f => f.id === selectedFileId);
      if (!file) {
        // If file not found in current list, try to reload files
        await loadFiles();
        return;
      }

      setActiveFile(file);

      // Load schema
      if (file.processingStatus === 'completed') {
        const fileSchema = await fileUploadService.getFileSchema(selectedFileId);
        setSchema(fileSchema);

        // Load chat history
        const history = await chatService.getChatHistory(selectedFileId);
        setMessages(history);
      }
    } catch (error) {
      console.error('Failed to load file data:', error);
    }
  };

  const handleFileSelect = (selectedFileId: string) => {
    navigate(`/chat/${selectedFileId}`);
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  const handleNewUpload = async (file: File) => {
    setUploadState('uploading');
    setUploadError(undefined);
    setUploadModalOpen(false);

    try {
      const validation = fileUploadService.validateFile(file);
      if (!validation.isValid) {
        setUploadError({
          code: 'INVALID_FORMAT',
          message: 'Invalid file',
          details: validation.errors.join(', '),
        });
        setUploadState('error');
        return;
      }

      const uploadResponse = await fileUploadService.uploadFile(
        file,
        (progress) => setUploadProgress(progress)
      );

      setUploadState('processing');
      
      // Create event source for processing updates
      if (!uploadResponse.success || !uploadResponse.data) {
        throw new Error(uploadResponse.error || 'Upload failed');
      }
      
      const eventSource = fileUploadService.createProcessingEventSource(uploadResponse.data.id);
      
      eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'complete') {
          setUploadState('success');
          eventSource.close();
          loadFiles(); // Refresh file list
          navigate(`/chat/${uploadResponse.data!.id}`);
        } else if (data.type === 'error') {
          setUploadError({
            code: 'PROCESSING_FAILED',
            message: 'Processing failed',
            details: data.error,
          });
          setUploadState('error');
          eventSource.close();
        }
      };

      eventSource.onerror = () => {
        setUploadError({
          code: 'NETWORK_ERROR',
          message: 'Connection lost',
          details: 'Lost connection during processing',
        });
        setUploadState('error');
        eventSource.close();
      };

    } catch (error) {
      console.error('Upload failed:', error);
      setUploadError({
        code: 'NETWORK_ERROR',
        message: 'Upload failed',
        details: error instanceof Error ? error.message : 'Unknown error',
      });
      setUploadState('error');
    }
  };

  const handleDeleteFile = async (fileIdToDelete: string) => {
    try {
      await fileUploadService.deleteFile(fileIdToDelete);
      await loadFiles();
      
      // If deleted file was active, navigate to another file or home
      if (fileId === fileIdToDelete) {
        const remainingFiles = files.filter(f => f.id !== fileIdToDelete);
        if (remainingFiles.length > 0) {
          navigate(`/chat/${remainingFiles[0].id}`, { replace: true });
        } else {
          navigate('/', { replace: true });
        }
      }
    } catch (error) {
      console.error('Failed to delete file:', error);
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!activeFile || !fileId) return;

    // Add user message
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      type: 'user',
      content: message,
      timestamp: new Date(),
      status: 'sent',
    };
    setMessages(prev => [...prev, userMessage]);

    // Show typing indicator
    setIsTyping(true);
    const typingMessage = chatService.createTypingMessage();
    setMessages(prev => [...prev, typingMessage]);

    try {
      const response = await chatService.sendMessage(
        message,
        fileId,
        settings.autoRunQueries
      );

      // Remove typing indicator
      setMessages(prev => prev.filter(m => m.id !== typingMessage.id));
      setIsTyping(false);

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Chat request failed');
      }

      // Add assistant response
      const assistantMessage: ChatMessage = {
        id: response.data.messageId,
        type: 'assistant',
        content: response.data.requiresConfirmation 
          ? `I'll run this query for you:\n\`\`\`sql\n${response.data.sqlQuery}\n\`\`\``
          : 'Query executed successfully!',
        timestamp: new Date(),
        status: 'sent',
        sqlQuery: response.data.sqlQuery,
        queryResults: response.data.results,
      };

      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      // Remove typing indicator and show error
      setMessages(prev => prev.filter(m => m.id !== typingMessage.id));
      setIsTyping(false);

      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
        status: 'error',
      };

      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const handleExecuteQuery = async (messageId: string, sqlQuery: string) => {
    if (!fileId) return;

    try {
      const result = await chatService.executeQuery(sqlQuery, fileId);
      
      if (!result.success || !result.data) {
        throw new Error(result.error || 'Query execution failed');
      }
      
      // Update the message with results
      setMessages(prev => prev.map(msg => 
        msg.id === messageId 
          ? { ...msg, queryResults: result.data }
          : msg
      ));
    } catch (error) {
      console.error('Query execution failed:', error);
    }
  };

  if (files.length === 0 && !uploadState) {
    // No files uploaded yet, redirect to landing
    navigate('/', { replace: true });
    return null;
  }

  return (
    <div className="h-screen bg-primary text-light-primary flex overflow-hidden">
      {/* Mobile Sidebar Overlay */}
      {isMobile && sidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div className={`
        ${isMobile ? 'fixed left-0 top-0 h-full z-50' : 'relative'} 
        ${sidebarOpen ? 'w-80' : 'w-0'} 
        transition-all duration-300 bg-secondary border-r border-surface
        ${isMobile && !sidebarOpen ? '-translate-x-full' : 'translate-x-0'}
      `}>
        <SchemaSidebar
          files={files}
          activeFileId={fileId}
          schema={schema}
          onFileSelect={handleFileSelect}
          onDeleteFile={handleDeleteFile}
          onNewUpload={() => setUploadModalOpen(true)}
          onOpenSettings={() => setSettingsModalOpen(true)}
          isMobile={isMobile}
          onClose={() => setSidebarOpen(false)}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="bg-secondary border-b border-surface px-4 py-3 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="small"
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2"
            >
              {sidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-primary" />
              <span className="font-medium truncate">
                {activeFile?.name || 'Select a file'}
              </span>
              {activeFile && (
                <span className="text-xs text-light-muted px-2 py-1 bg-surface rounded">
                  {activeFile.rowCount?.toLocaleString()} rows
                </span>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="small"
              onClick={() => setUploadModalOpen(true)}
              className="flex items-center gap-2"
            >
              <Upload className="h-4 w-4" />
              {!isMobile && 'Upload'}
            </Button>
            
            <Button
              variant="ghost"
              size="small"
              onClick={() => setSettingsModalOpen(true)}
              className="p-2"
            >
              <Settings className="h-4 w-4" />
            </Button>

            <ThemeToggle theme={theme} onToggle={onToggleTheme} />
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 min-h-0">
          {activeFile && schema ? (
            <ChatWindow
              messages={messages}
              isTyping={isTyping}
              onSendMessage={handleSendMessage}
              onExecuteQuery={handleExecuteQuery}
              schema={schema}
              settings={settings}
            />
          ) : (
            <div className="h-full flex items-center justify-center">
              <div className="text-center space-y-4 max-w-md mx-auto px-4">
                <MessageSquare className="h-12 w-12 text-light-muted mx-auto" />
                <h3 className="text-lg font-medium text-light-primary">
                  {activeFile ? 'Processing File...' : 'Select a File to Start Chatting'}
                </h3>
                <p className="text-sm text-light-muted">
                  {activeFile 
                    ? 'Your file is being processed. This usually takes a few moments.'
                    : 'Choose a CSV file from the sidebar or upload a new one to begin asking questions about your data.'
                  }
                </p>
                {!activeFile && (
                  <Button
                    variant="primary"
                    onClick={() => setUploadModalOpen(true)}
                    className="flex items-center gap-2"
                  >
                    <Upload className="h-4 w-4" />
                    Upload CSV File
                  </Button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModalOpen}
        onClose={() => setUploadModalOpen(false)}
        title="Upload New CSV File"
        size="medium"
      >
        <FileUploadZone
          onUpload={handleNewUpload}
          maxSize={100}
          acceptedTypes={['.csv', '.tsv']}
          state={uploadState}
          progress={uploadProgress}
          error={uploadError}
        />
        
        {uploadState === 'error' && (
          <div className="mt-4 flex justify-end">
            <Button
              variant="primary"
              onClick={() => {
                setUploadState('idle');
                setUploadError(undefined);
              }}
            >
              Try Again
            </Button>
          </div>
        )}
      </Modal>

      {/* Settings Modal */}
      <Modal
        isOpen={settingsModalOpen}
        onClose={() => setSettingsModalOpen(false)}
        title="Settings"
        size="medium"
      >
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-light-primary mb-2">
              Query Result Limit
            </label>
            <select
              value={settings.rowLimit}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                rowLimit: parseInt(e.target.value)
              }))}
              className="form-input"
            >
              <option value={100}>100 rows</option>
              <option value={500}>500 rows</option>
              <option value={1000}>1,000 rows</option>
              <option value={5000}>5,000 rows</option>
            </select>
          </div>

          <div>
            <label className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={settings.autoRunQueries}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  autoRunQueries: e.target.checked
                }))}
                className="form-checkbox"
              />
              <span className="text-sm text-light-secondary">
                Auto-run queries (skip confirmation)
              </span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-light-primary mb-2">
              Export Format
            </label>
            <select
              value={settings.exportFormat}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                exportFormat: e.target.value as 'csv' | 'json'
              }))}
              className="form-input"
            >
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
          </div>
        </div>
      </Modal>
    </div>
  );
}