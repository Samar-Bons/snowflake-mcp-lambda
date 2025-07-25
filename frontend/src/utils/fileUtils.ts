// ABOUTME: Utility functions for file name processing and display
// ABOUTME: Handles simplifying meaningful file IDs for UI display

interface FileDisplayName {
  id: string;
  originalName: string;
  displayName: string;
}

/**
 * Extract clean filename from the full meaningful file ID
 * Example: "sales_data_q4_2024_20250725_033940_da88" -> "sales_data_q4_2024.csv"
 */
export function extractCleanFilename(fullFileId: string): string {
  // Handle old UUID format (backwards compatibility)
  if (fullFileId.match(/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}/)) {
    // For old UUIDs, we might have the filename appended
    const parts = fullFileId.split('_');
    if (parts.length > 1) {
      const filename = parts.slice(1).join('_');
      return filename.endsWith('.csv') ? filename : `${filename}.csv`;
    }
    return 'data.csv';
  }

  // Handle new meaningful file IDs
  // Format: cleanname_YYYYMMDD_HHMMSS_shortid_originalname.csv
  // We want to extract just the original filename
  
  const parts = fullFileId.split('_');
  
  // If it ends with .csv, it's likely the full stored name
  if (fullFileId.endsWith('.csv')) {
    // Try to find where the timestamp pattern starts
    let timestampIndex = -1;
    for (let i = 0; i < parts.length; i++) {
      // Look for YYYYMMDD pattern
      if (parts[i] && parts[i].match(/^\d{8}$/)) {
        timestampIndex = i;
        break;
      }
    }
    
    if (timestampIndex > 0) {
      // Get the clean name part before timestamp
      const cleanName = parts.slice(0, timestampIndex).join('_');
      return `${cleanName}.csv`;
    }
  }
  
  // For file IDs without extension (from URL), extract base name
  let timestampIndex = -1;
  for (let i = 0; i < parts.length; i++) {
    if (parts[i] && parts[i].match(/^\d{8}$/)) {
      timestampIndex = i;
      break;
    }
  }
  
  if (timestampIndex > 0) {
    const cleanName = parts.slice(0, timestampIndex).join('_');
    // Handle edge case where name becomes empty after cleaning
    const finalName = cleanName || fullFileId.split('_')[0] || 'data';
    return `${finalName}.csv`;
  }
  
  // Fallback - use the whole thing
  return fullFileId.endsWith('.csv') ? fullFileId : `${fullFileId}.csv`;
}

/**
 * Generate display names for a list of files, handling duplicates
 * Adds numeric suffix only when there are actual duplicates
 */
export function generateFileDisplayNames(files: Array<{ id: string; name: string }>): FileDisplayName[] {
  const nameCount = new Map<string, number>();
  const nameSeen = new Map<string, number>();
  
  // First pass: count occurrences of each clean name
  files.forEach(file => {
    const cleanName = extractCleanFilename(file.name);
    nameCount.set(cleanName, (nameCount.get(cleanName) || 0) + 1);
  });
  
  // Second pass: generate display names
  return files.map(file => {
    const cleanName = extractCleanFilename(file.name);
    const count = nameCount.get(cleanName) || 1;
    
    let displayName = cleanName;
    
    // Only add suffix if there are duplicates
    if (count > 1) {
      const seen = (nameSeen.get(cleanName) || 0) + 1;
      nameSeen.set(cleanName, seen);
      
      // Remove .csv extension, add suffix, then re-add extension
      const baseName = cleanName.replace(/\.csv$/, '');
      displayName = `${baseName} (${seen}).csv`;
    }
    
    return {
      id: file.id,
      originalName: file.name,
      displayName
    };
  });
}

/**
 * Get simplified display name for a single file
 * Note: This doesn't handle duplicates - use generateFileDisplayNames for that
 */
export function getFileDisplayName(filename: string): string {
  return extractCleanFilename(filename);
}

/**
 * Extract base filename without extension
 */
export function getBaseFilename(filename: string): string {
  const clean = extractCleanFilename(filename);
  return clean.replace(/\.[^/.]+$/, '');
}