// ABOUTME: Main dashboard page with complete chat interface and schema explorer
// ABOUTME: Integrates ChatWindow and SchemaSidebar for full Snowflake interaction experience

import { useState } from 'react';
import { ChatWindow } from '../components/chat/ChatWindow';
import { SchemaSidebar } from '../components/schema/SchemaSidebar';
import { Header } from '../components/layout/Header';

export function DashboardPage() {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  return (
    <div className="h-screen flex flex-col bg-slate-900">
      {/* Header */}
      <Header />

      {/* Main content area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Schema Sidebar */}
        <SchemaSidebar
          isCollapsed={isSidebarCollapsed}
          onToggle={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        />

        {/* Chat Area */}
        <div className="flex-1">
          <ChatWindow />
        </div>
      </div>
    </div>
  );
}
