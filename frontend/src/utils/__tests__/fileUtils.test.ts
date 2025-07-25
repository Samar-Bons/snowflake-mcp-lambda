// ABOUTME: Tests for file utility functions that simplify file display names
// ABOUTME: Verifies filename extraction, duplicate handling, and edge cases

import { describe, it, expect } from 'vitest';
import {
  extractCleanFilename,
  generateFileDisplayNames,
  getFileDisplayName,
  getBaseFilename
} from '../fileUtils';

describe('fileUtils', () => {
  describe('extractCleanFilename', () => {
    it('should extract clean filename from new meaningful file ID', () => {
      const fileId = 'sales_data_q4_2024_20250725_033940_da88';
      expect(extractCleanFilename(fileId)).toBe('sales_data_q4_2024.csv');
    });

    it('should handle file ID with .csv extension', () => {
      const fileId = 'sales_data_q4_2024_20250725_033940_da88_sales_data_q4_2024.csv';
      expect(extractCleanFilename(fileId)).toBe('sales_data_q4_2024.csv');
    });

    it('should handle old UUID format', () => {
      const uuid = 'e9739780-5938-4b26-b952-52b52e0896bb';
      expect(extractCleanFilename(uuid)).toBe('data.csv');
    });

    it('should handle old UUID with filename appended', () => {
      const uuidWithName = 'e9739780-5938-4b26-b952-52b52e0896bb_customer_data';
      expect(extractCleanFilename(uuidWithName)).toBe('customer_data.csv');
    });

    it('should handle filename with underscores', () => {
      const fileId = 'customer_order_data_2024_20250725_033940_da88';
      expect(extractCleanFilename(fileId)).toBe('customer_order_data_2024.csv');
    });

    it('should handle filename with no timestamp', () => {
      const fileId = 'simple_filename';
      expect(extractCleanFilename(fileId)).toBe('simple_filename.csv');
    });

    it('should handle empty string', () => {
      expect(extractCleanFilename('')).toBe('.csv');
    });

    it('should handle filename already ending with .csv', () => {
      const fileId = 'data_export.csv';
      expect(extractCleanFilename(fileId)).toBe('data_export.csv');
    });

    it('should handle complex meaningful ID', () => {
      const fileId = 'monthly_sales_report_q4_2024_20250725_143022_abc1';
      expect(extractCleanFilename(fileId)).toBe('monthly_sales_report_q4_2024.csv');
    });

    it('should handle single word before timestamp', () => {
      const fileId = 'data_20250725_143022_abc1';
      expect(extractCleanFilename(fileId)).toBe('data.csv');
    });
  });

  describe('generateFileDisplayNames', () => {
    it('should generate display names without suffixes when no duplicates', () => {
      const files = [
        { id: '1', name: 'sales_data_20250725_033940_da88' },
        { id: '2', name: 'customer_data_20250725_033941_da89' },
        { id: '3', name: 'product_list_20250725_033942_da90' }
      ];

      const result = generateFileDisplayNames(files);

      expect(result).toHaveLength(3);
      expect(result[0]).toEqual({
        id: '1',
        originalName: 'sales_data_20250725_033940_da88',
        displayName: 'sales_data.csv'
      });
      expect(result[1]).toEqual({
        id: '2',
        originalName: 'customer_data_20250725_033941_da89',
        displayName: 'customer_data.csv'
      });
      expect(result[2]).toEqual({
        id: '3',
        originalName: 'product_list_20250725_033942_da90',
        displayName: 'product_list.csv'
      });
    });

    it('should add numeric suffixes for duplicate names', () => {
      const files = [
        { id: '1', name: 'customer_data_20250725_033940_da88' },
        { id: '2', name: 'customer_data_20250725_033941_da89' },
        { id: '3', name: 'customer_data_20250725_033942_da90' }
      ];

      const result = generateFileDisplayNames(files);

      expect(result).toHaveLength(3);
      expect(result[0].displayName).toBe('customer_data (1).csv');
      expect(result[1].displayName).toBe('customer_data (2).csv');
      expect(result[2].displayName).toBe('customer_data (3).csv');
    });

    it('should handle mix of unique and duplicate names', () => {
      const files = [
        { id: '1', name: 'sales_data_20250725_033940_da88' },
        { id: '2', name: 'customer_data_20250725_033941_da89' },
        { id: '3', name: 'sales_data_20250725_033942_da90' },
        { id: '4', name: 'product_list_20250725_033943_da91' }
      ];

      const result = generateFileDisplayNames(files);

      expect(result[0].displayName).toBe('sales_data (1).csv');
      expect(result[1].displayName).toBe('customer_data.csv');
      expect(result[2].displayName).toBe('sales_data (2).csv');
      expect(result[3].displayName).toBe('product_list.csv');
    });

    it('should handle old UUID format files', () => {
      const files = [
        { id: '1', name: 'e9739780-5938-4b26-b952-52b52e0896bb' },
        { id: '2', name: 'sales_data_20250725_033940_da88' },
        { id: '3', name: 'e9739780-5938-4b26-b952-52b52e0896bb_customer_data' }
      ];

      const result = generateFileDisplayNames(files);

      expect(result[0].displayName).toBe('data.csv');
      expect(result[1].displayName).toBe('sales_data.csv');
      expect(result[2].displayName).toBe('customer_data.csv');
    });

    it('should handle empty file list', () => {
      const result = generateFileDisplayNames([]);
      expect(result).toEqual([]);
    });

    it('should handle files with .csv extension in name', () => {
      const files = [
        { id: '1', name: 'report.csv' },
        { id: '2', name: 'report_20250725_033940_da88.csv' },
        { id: '3', name: 'report_20250725_033941_da89' }
      ];

      const result = generateFileDisplayNames(files);

      expect(result[0].displayName).toBe('report (1).csv');
      expect(result[1].displayName).toBe('report (2).csv');
      expect(result[2].displayName).toBe('report (3).csv');
    });

    it('should preserve original file properties', () => {
      const files = [
        { id: 'abc123', name: 'data_20250725_033940_da88' }
      ];

      const result = generateFileDisplayNames(files);

      expect(result[0].id).toBe('abc123');
      expect(result[0].originalName).toBe('data_20250725_033940_da88');
    });
  });

  describe('getFileDisplayName', () => {
    it('should return simplified name for single file', () => {
      expect(getFileDisplayName('sales_data_20250725_033940_da88')).toBe('sales_data.csv');
    });

    it('should handle various input formats', () => {
      expect(getFileDisplayName('data.csv')).toBe('data.csv');
      expect(getFileDisplayName('e9739780-5938-4b26-b952-52b52e0896bb')).toBe('data.csv');
      expect(getFileDisplayName('report_final_v2_20250725_033940_da88')).toBe('report_final_v2.csv');
    });

    it('should not add duplicate suffixes (single file context)', () => {
      // This function doesn't handle duplicates - that's done by generateFileDisplayNames
      expect(getFileDisplayName('data_20250725_033940_da88')).toBe('data.csv');
      expect(getFileDisplayName('data_20250725_033941_da89')).toBe('data.csv');
    });
  });

  describe('getBaseFilename', () => {
    it('should extract base filename without extension', () => {
      expect(getBaseFilename('sales_data_20250725_033940_da88')).toBe('sales_data');
      expect(getBaseFilename('report.csv')).toBe('report');
      expect(getBaseFilename('data_export_final_20250725_033940_da88.csv')).toBe('data_export_final');
    });

    it('should handle files with multiple dots', () => {
      expect(getBaseFilename('report.final.data_20250725_033940_da88')).toBe('report.final.data');
      expect(getBaseFilename('my.file.name.csv')).toBe('my.file.name');
    });

    it('should handle edge cases', () => {
      expect(getBaseFilename('')).toBe('');
      expect(getBaseFilename('.csv')).toBe('');
      expect(getBaseFilename('noextension')).toBe('noextension');
    });

    it('should handle old UUID format', () => {
      expect(getBaseFilename('e9739780-5938-4b26-b952-52b52e0896bb')).toBe('data');
      expect(getBaseFilename('e9739780-5938-4b26-b952-52b52e0896bb_myfile')).toBe('myfile');
    });
  });

  describe('edge cases and special scenarios', () => {
    it('should handle files with only timestamp and ID', () => {
      const fileId = '20250725_033940_da88';
      expect(extractCleanFilename(fileId)).toBe('20250725_033940_da88.csv');
    });

    it('should handle very long filenames', () => {
      const longName = 'this_is_a_very_long_filename_that_might_cause_issues_20250725_033940_da88';
      expect(extractCleanFilename(longName)).toBe('this_is_a_very_long_filename_that_might_cause_issues.csv');
    });

    it('should handle special characters that might appear', () => {
      const files = [
        { id: '1', name: 'data-export_20250725_033940_da88' },
        { id: '2', name: 'data.export_20250725_033941_da89' },
        { id: '3', name: 'data export_20250725_033942_da90' }
      ];

      const result = generateFileDisplayNames(files);
      
      expect(result[0].displayName).toBe('data-export.csv');
      expect(result[1].displayName).toBe('data.export.csv');
      expect(result[2].displayName).toBe('data export.csv');
    });

    it('should handle malformed meaningful IDs gracefully', () => {
      const malformed = [
        { id: '1', name: '_20250725_033940_' },
        { id: '2', name: 'data__20250725__033940__da88' },
        { id: '3', name: '___' }
      ];

      const result = generateFileDisplayNames(malformed);
      
      expect(result[0].displayName).toBe('data.csv'); // Empty prefix becomes 'data' fallback
      expect(result[1].displayName).toBe('data_.csv'); // 'data_' extracted from malformed ID
      expect(result[2].displayName).toBe('___.csv'); // Preserved as-is
    });

    it('should handle mixed case consistently', () => {
      const files = [
        { id: '1', name: 'Customer_Data_20250725_033940_da88' },
        { id: '2', name: 'CUSTOMER_DATA_20250725_033941_da89' },
        { id: '3', name: 'customer_data_20250725_033942_da90' }
      ];

      const result = generateFileDisplayNames(files);
      
      // All should be treated as different files due to case sensitivity
      expect(result[0].displayName).toBe('Customer_Data.csv');
      expect(result[1].displayName).toBe('CUSTOMER_DATA.csv');
      expect(result[2].displayName).toBe('customer_data.csv');
    });
  });
});