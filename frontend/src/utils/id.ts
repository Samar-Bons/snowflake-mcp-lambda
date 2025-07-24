// ABOUTME: Utility functions for generating unique identifiers
// ABOUTME: Ensures uniqueness for React keys and message IDs

/**
 * Generate a unique ID using crypto.randomUUID if available,
 * falling back to a timestamp + random number combination
 */
export function generateUniqueId(prefix?: string): string {
  let uniqueId: string;

  // Use crypto.randomUUID if available (modern browsers)
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    uniqueId = crypto.randomUUID();
  } else {
    // Fallback: timestamp + random number for better uniqueness
    const timestamp = Date.now();
    const random = Math.random().toString(36).substring(2, 9);
    uniqueId = `${timestamp}-${random}`;
  }

  return prefix ? `${prefix}-${uniqueId}` : uniqueId;
}

/**
 * Generate a unique message ID
 */
export function generateMessageId(type: 'user' | 'assistant' | 'error' | 'typing'): string {
  return generateUniqueId(type);
}
