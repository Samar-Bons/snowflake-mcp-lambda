// ABOUTME: Main application layout wrapper component
// ABOUTME: Provides consistent structure with header and main content area

import type { ReactNode } from 'react';
import { Header } from './Header';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-slate-900 dark">
      <Header />
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
}
