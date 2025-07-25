// ABOUTME: Main chat layout with responsive sidebar and chat area
// ABOUTME: Handles desktop sidebar + mobile bottom navigation for chat interface

import { useState, useMemo } from 'react';
import {
  Menu,
  X,
  FileSpreadsheet,
  Database,
  Settings,
  Upload,
  MessageSquare
} from 'lucide-react';
import { Button } from '../ui/Button';
import { UploadedFile, TableSchema } from '../../types';
import { generateFileDisplayNames } from '../../utils/fileUtils';

interface ChatLayoutProps {
  files: UploadedFile[];
  activeFile: UploadedFile | null;
  schema: TableSchema | null;
  children: React.ReactNode;
  onFileSelect: (fileId: string) => void;
  onUploadNew: () => void;
  onSettingsOpen: () => void;
}

export function ChatLayout({
  files,
  activeFile,
  schema,
  children,
  onFileSelect,
  onUploadNew,
  onSettingsOpen
}: ChatLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'files' | 'schema' | 'settings'>('files');

  const closeSidebar = () => setSidebarOpen(false);

  // Generate display names for all files
  const fileDisplayNames = useMemo(() => {
    return generateFileDisplayNames(files);
  }, [files]);

  // Get display name for active file
  const activeFileDisplayName = useMemo(() => {
    if (!activeFile) return null;
    return fileDisplayNames.find(f => f.id === activeFile.id)?.displayName || activeFile.name;
  }, [activeFile, fileDisplayNames]);

  return (
    <div className="h-screen bg-secondary-dark flex overflow-hidden">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex lg:flex-shrink-0">
        <div className="flex flex-col w-80">
          <Sidebar
            files={files}
            fileDisplayNames={fileDisplayNames}
            activeFile={activeFile}
            schema={schema}
            activeTab={activeTab}
            onTabChange={setActiveTab}
            onFileSelect={onFileSelect}
            onUploadNew={onUploadNew}
            onSettingsOpen={onSettingsOpen}
          />
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div className="lg:hidden fixed inset-0 z-50 flex">
          <div className="fixed inset-0 bg-black bg-opacity-50" onClick={closeSidebar} />
          <div className="relative flex flex-col w-80 bg-secondary-dark shadow-xl">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <Button
                variant="ghost"
                size="small"
                onClick={closeSidebar}
                className="text-white hover:text-light-primary"
              >
                <X className="h-6 w-6" />
              </Button>
            </div>
            <Sidebar
              files={files}
              fileDisplayNames={fileDisplayNames}
              activeFile={activeFile}
              schema={schema}
              activeTab={activeTab}
              onTabChange={setActiveTab}
              onFileSelect={onFileSelect}
              onUploadNew={onUploadNew}
              onSettingsOpen={onSettingsOpen}
            />
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile Header */}
        <div className="lg:hidden bg-surface border-b border-surface px-4 py-3 flex items-center justify-between">
          <Button
            variant="ghost"
            size="small"
            onClick={() => setSidebarOpen(true)}
            className="text-light-primary"
          >
            <Menu className="h-5 w-5" />
          </Button>

          <div className="flex items-center gap-2">
            {activeFile && activeFileDisplayName && (
              <>
                <FileSpreadsheet className="h-4 w-4 text-blue-primary" />
                <span className="text-sm font-medium text-light-primary truncate max-w-32">
                  {activeFileDisplayName}
                </span>
              </>
            )}
          </div>

          <Button
            variant="ghost"
            size="small"
            onClick={onSettingsOpen}
            className="text-light-primary"
          >
            <Settings className="h-5 w-5" />
          </Button>
        </div>

        {/* Chat Content */}
        <div className="flex-1 overflow-hidden">
          {children}
        </div>
      </div>
    </div>
  );
}

// Sidebar Component
interface SidebarProps {
  files: UploadedFile[];
  fileDisplayNames: Array<{ id: string; originalName: string; displayName: string }>;
  activeFile: UploadedFile | null;
  schema: TableSchema | null;
  activeTab: 'files' | 'schema' | 'settings';
  onTabChange: (tab: 'files' | 'schema' | 'settings') => void;
  onFileSelect: (fileId: string) => void;
  onUploadNew: () => void;
  onSettingsOpen: () => void;
}

function Sidebar({
  files,
  fileDisplayNames,
  activeFile,
  schema,
  activeTab,
  onTabChange,
  onFileSelect,
  onUploadNew,
  onSettingsOpen
}: SidebarProps) {
  const tabs = [
    { id: 'files' as const, label: 'Files', icon: FileSpreadsheet },
    { id: 'schema' as const, label: 'Schema', icon: Database },
    { id: 'settings' as const, label: 'Settings', icon: Settings },
  ];

  return (
    <div className="h-full bg-secondary-dark border-r border-surface flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-surface">
        <div className="flex items-center gap-2">
          <MessageSquare className="h-6 w-6 text-blue-primary" />
          <h1 className="text-lg font-semibold text-light-primary">Data Chat</h1>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-surface">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? 'text-blue-primary border-b-2 border-blue-primary bg-surface/30'
                : 'text-light-muted hover:text-light-primary hover:bg-surface/20'
            }`}
          >
            <tab.icon className="h-4 w-4" />
            <span className="hidden sm:inline">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-y-auto p-4">
        {activeTab === 'files' && (
          <FilesPanel
            files={files}
            fileDisplayNames={fileDisplayNames}
            activeFile={activeFile}
            onFileSelect={onFileSelect}
            onUploadNew={onUploadNew}
          />
        )}

        {activeTab === 'schema' && (
          <SchemaPanel schema={schema} />
        )}

        {activeTab === 'settings' && (
          <SettingsPanel onSettingsOpen={onSettingsOpen} />
        )}
      </div>
    </div>
  );
}

// Files Panel
interface FilesPanelProps {
  files: UploadedFile[];
  fileDisplayNames: Array<{ id: string; originalName: string; displayName: string }>;
  activeFile: UploadedFile | null;
  onFileSelect: (fileId: string) => void;
  onUploadNew: () => void;
}

function FilesPanel({ files, fileDisplayNames, activeFile, onFileSelect, onUploadNew }: FilesPanelProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-light-primary">Uploaded Files</h3>
        <Button
          variant="outline"
          size="small"
          onClick={onUploadNew}
          className="text-xs"
        >
          <Upload className="h-3 w-3 mr-1" />
          New
        </Button>
      </div>

      {files.length === 0 ? (
        <div className="text-center py-8">
          <FileSpreadsheet className="h-8 w-8 text-light-muted mx-auto mb-2" />
          <p className="text-sm text-light-muted">No files uploaded yet</p>
          <Button
            variant="primary"
            size="small"
            onClick={onUploadNew}
            className="mt-2"
          >
            Upload CSV
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          {files.map((file) => {
            const displayName = fileDisplayNames.find(f => f.id === file.id)?.displayName || file.name;
            return (
              <button
                key={file.id}
                onClick={() => onFileSelect(file.id)}
                className={`w-full p-3 rounded-lg border text-left transition-colors ${
                  activeFile?.id === file.id
                    ? 'border-blue-primary bg-blue-primary/10 text-light-primary'
                    : 'border-surface bg-surface/30 text-light-secondary hover:bg-surface/50 hover:border-surface-elevated'
                }`}
              >
                <div className="flex items-start gap-3">
                  <FileSpreadsheet className="h-4 w-4 text-blue-primary mt-0.5 flex-shrink-0" />
                  <div className="min-w-0 flex-1">
                    <p className="text-sm font-medium truncate">{displayName}</p>
                    <p className="text-xs text-light-muted">
                      {file.estimatedRows?.toLocaleString()} rows • {(file.size / 1024 / 1024).toFixed(1)} MB
                    </p>
                    <p className="text-xs text-light-subtle">
                      {file.uploadedAt ? new Date(file.uploadedAt).toLocaleDateString() : 'Processing...'}
                    </p>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}

// Schema Panel
interface SchemaPanelProps {
  schema: TableSchema | null;
}

function SchemaPanel({ schema }: SchemaPanelProps) {
  if (!schema) {
    return (
      <div className="text-center py-8">
        <Database className="h-8 w-8 text-light-muted mx-auto mb-2" />
        <p className="text-sm text-light-muted">No schema available</p>
        <p className="text-xs text-light-subtle">Upload a file to see its structure</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-sm font-medium text-light-primary mb-2">Table Structure</h3>
        <div className="text-xs text-light-muted">
          {schema.rowCount.toLocaleString()} rows • {schema.columns.length} columns
        </div>
      </div>

      <div className="space-y-2">
        {schema.columns.map((column) => (
          <div
            key={column.name}
            className="p-2 rounded border border-surface bg-surface/20"
          >
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-light-primary truncate">
                {column.name}
              </span>
              <span className="text-xs text-blue-primary">
                {column.type.toUpperCase()}
              </span>
            </div>
            {column.nullable && (
              <div className="text-xs text-light-subtle mt-1">Nullable</div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// Settings Panel
interface SettingsPanelProps {
  onSettingsOpen: () => void;
}

function SettingsPanel({ onSettingsOpen }: SettingsPanelProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium text-light-primary">Quick Settings</h3>

      <div className="space-y-3">
        <div className="p-3 rounded-lg border border-surface bg-surface/20">
          <div className="flex items-center justify-between">
            <span className="text-sm text-light-primary">Row Limit</span>
            <span className="text-sm text-blue-primary">500</span>
          </div>
          <p className="text-xs text-light-muted mt-1">Maximum rows per query</p>
        </div>

        <div className="p-3 rounded-lg border border-surface bg-surface/20">
          <div className="flex items-center justify-between">
            <span className="text-sm text-light-primary">Auto-run</span>
            <span className="text-sm text-success">Enabled</span>
          </div>
          <p className="text-xs text-light-muted mt-1">Execute queries automatically</p>
        </div>

        <Button
          variant="outline"
          onClick={onSettingsOpen}
          className="w-full"
        >
          <Settings className="h-4 w-4 mr-2" />
          All Settings
        </Button>
      </div>
    </div>
  );
}
