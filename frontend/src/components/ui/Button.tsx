// ABOUTME: Reusable Button component with multiple variants and loading states
// ABOUTME: Follows the design system styling with primary, secondary, outline, and ghost variants

import React from 'react';
import { Loader2 } from 'lucide-react';
import { ButtonProps } from '../../types';
import { clsx } from 'clsx';

export function Button({
  children,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  onClick,
  type = 'button',
  className,
  ...props
}: ButtonProps) {
  const baseClasses = 'btn';
  
  const variantClasses = {
    primary: 'btn--primary',
    secondary: 'btn--secondary',
    outline: 'btn--outline',
    ghost: 'btn--ghost',
  };

  const sizeClasses = {
    small: 'btn--small',
    medium: '',
    large: 'btn--large',
  };

  const buttonClasses = clsx(
    baseClasses,
    variantClasses[variant],
    sizeClasses[size],
    {
      'opacity-50 cursor-not-allowed': disabled || loading,
    },
    className
  );

  return (
    <button
      type={type}
      className={buttonClasses}
      disabled={disabled || loading}
      onClick={onClick}
      {...props}
    >
      {loading && (
        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
      )}
      {children}
    </button>
  );
}