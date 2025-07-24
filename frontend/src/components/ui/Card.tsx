// ABOUTME: Reusable Card component with elevation and interactive variants
// ABOUTME: Provides consistent styling for content containers throughout the app

import { ReactNode } from 'react';
import { clsx } from 'clsx';

interface CardProps {
  children: ReactNode;
  elevated?: boolean;
  interactive?: boolean;
  className?: string;
  onClick?: () => void;
}

export function Card({
  children,
  elevated = false,
  interactive = false,
  className,
  onClick
}: CardProps) {
  const cardClasses = clsx(
    'card',
    {
      'card--elevated': elevated,
      'card--interactive': interactive,
    },
    className
  );

  return (
    <div className={cardClasses} onClick={onClick}>
      {children}
    </div>
  );
}

interface CardHeaderProps {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
  className?: string;
}

export function CardHeader({ title, subtitle, actions, className }: CardHeaderProps) {
  return (
    <div className={clsx('flex items-start justify-between mb-4', className)}>
      <div className="flex-1">
        <h3 className="text-xl font-normal text-light-primary mb-1">
          {title}
        </h3>
        {subtitle && (
          <p className="text-sm text-light-muted">
            {subtitle}
          </p>
        )}
      </div>
      {actions && (
        <div className="ml-4 flex-shrink-0">
          {actions}
        </div>
      )}
    </div>
  );
}

interface CardContentProps {
  children: ReactNode;
  className?: string;
}

export function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={clsx('text-light-secondary mb-6', className)}>
      {children}
    </div>
  );
}

interface CardActionsProps {
  children: ReactNode;
  className?: string;
}

export function CardActions({ children, className }: CardActionsProps) {
  return (
    <div className={clsx('flex gap-3 flex-wrap', className)}>
      {children}
    </div>
  );
}
