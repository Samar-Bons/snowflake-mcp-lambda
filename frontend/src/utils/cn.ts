// ABOUTME: Class name utility for combining and conditionally applying CSS classes
// ABOUTME: Uses clsx for conditional logic and can be extended with tailwind-merge

import { clsx, type ClassValue } from 'clsx';

/**
 * Combines class names with conditional logic
 * Can be extended with tailwind-merge for intelligent Tailwind class merging
 */
export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}
