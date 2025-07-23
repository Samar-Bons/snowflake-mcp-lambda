// ABOUTME: Theme toggle component for switching between dark and light modes
// ABOUTME: Styled to match the design system with smooth icon transitions

import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { clsx } from 'clsx';

interface ThemeToggleProps {
  theme: 'dark' | 'light';
  onToggle: () => void;
  variant?: 'default' | 'hero';
  className?: string;
}

export function ThemeToggle({ 
  theme, 
  onToggle, 
  variant = 'default',
  className 
}: ThemeToggleProps) {
  const baseClasses = clsx(
    'relative bg-none border-2 border-surface-elevated rounded-full w-12 h-12 cursor-pointer transition-all duration-300',
    'flex items-center justify-center text-light-muted',
    'hover:border-blue-primary hover:text-blue-primary hover:rotate-180',
    'focus:outline-none focus:ring-2 focus:ring-blue-primary focus:ring-offset-2 focus:ring-offset-primary',
    {
      'absolute top-6 right-6 z-10 bg-surface/80 backdrop-blur-sm border-white/10 hover:bg-surface-elevated/90': variant === 'hero',
    },
    className
  );

  return (
    <button
      onClick={onToggle}
      className={baseClasses}
      aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
    >
      <Sun 
        className={clsx(
          'absolute h-5 w-5 transition-all duration-300',
          theme === 'light' 
            ? 'opacity-100 rotate-0 scale-100' 
            : 'opacity-0 -rotate-90 scale-50'
        )}
      />
      <Moon 
        className={clsx(
          'absolute h-5 w-5 transition-all duration-300',
          theme === 'dark' 
            ? 'opacity-100 rotate-0 scale-100' 
            : 'opacity-0 rotate-90 scale-50'
        )}
      />
    </button>
  );
}