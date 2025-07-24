// ABOUTME: Modal component with backdrop and animation for dialogs and confirmations
// ABOUTME: Provides consistent modal behavior with focus management and escape key handling

import { useEffect, ReactNode } from 'react';
import { X } from 'lucide-react';
import { clsx } from 'clsx';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title?: string;
  children: ReactNode;
  size?: 'small' | 'medium' | 'large';
  className?: string;
}

export function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'medium',
  className
}: ModalProps) {
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const sizeClasses = {
    small: 'max-w-md',
    medium: 'max-w-lg',
    large: 'max-w-2xl',
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className={clsx(
          'modal-content w-full m-4',
          sizeClasses[size],
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
        {title && (
          <div className="flex items-center justify-between p-6 border-b border-surface">
            <h2 className="text-xl font-normal text-light-primary">
              {title}
            </h2>
            <button
              onClick={onClose}
              className="p-2 text-light-muted hover:text-light-primary hover:bg-surface rounded-sm transition-all"
            >
              <X className="h-5 w-5" />
              <span className="sr-only">Close</span>
            </button>
          </div>
        )}

        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
}

interface ModalHeaderProps {
  title: string;
  subtitle?: string;
  onClose: () => void;
}

export function ModalHeader({ title, subtitle, onClose }: ModalHeaderProps) {
  return (
    <div className="flex items-start justify-between p-6 border-b border-surface">
      <div>
        <h2 className="text-xl font-normal text-light-primary mb-1">
          {title}
        </h2>
        {subtitle && (
          <p className="text-sm text-light-muted">
            {subtitle}
          </p>
        )}
      </div>
      <button
        onClick={onClose}
        className="p-2 text-light-muted hover:text-light-primary hover:bg-surface rounded-sm transition-all"
      >
        <X className="h-5 w-5" />
        <span className="sr-only">Close</span>
      </button>
    </div>
  );
}

interface ModalFooterProps {
  children: ReactNode;
  className?: string;
}

export function ModalFooter({ children, className }: ModalFooterProps) {
  return (
    <div className={clsx(
      'flex gap-3 justify-end p-6 border-t border-surface',
      className
    )}>
      {children}
    </div>
  );
}
