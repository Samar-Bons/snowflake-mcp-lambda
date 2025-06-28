// ABOUTME: React hook for managing performance metrics collection and measurement
// ABOUTME: Provides utilities for timing operations and collecting browser performance data

import { useCallback, useRef, useState } from 'react';

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  type: 'timing' | 'counter' | 'gauge';
  tags?: Record<string, string>;
}

interface ActiveMeasurement {
  name: string;
  startTime: number;
  metadata?: Record<string, any>;
}

export function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const activeMeasurements = useRef<Map<string, ActiveMeasurement>>(new Map());
  const metricsBuffer = useRef<PerformanceMetric[]>([]);

  // Start a performance measurement
  const startMeasure = useCallback((name: string, metadata?: Record<string, any>) => {
    const measureId = `${name}_${Date.now()}_${Math.random()}`;

    activeMeasurements.current.set(measureId, {
      name,
      startTime: performance.now(),
      metadata,
    });

    return measureId;
  }, []);

  // End a performance measurement
  const endMeasure = useCallback((measureId: string, tags?: Record<string, string>) => {
    const measurement = activeMeasurements.current.get(measureId);

    if (!measurement) {
      console.warn(`No active measurement found for ID: ${measureId}`);
      return null;
    }

    const endTime = performance.now();
    const duration = endTime - measurement.startTime;

    const metric: PerformanceMetric = {
      name: measurement.name,
      value: duration,
      timestamp: endTime,
      type: 'timing',
      tags,
    };

    // Add to buffer
    metricsBuffer.current.push(metric);

    // Update state with recent metrics (keep last 100)
    setMetrics(current => [...current, metric].slice(-100));

    // Clean up
    activeMeasurements.current.delete(measureId);

    return duration;
  }, []);

  // Record a simple metric value
  const recordMetric = useCallback((
    name: string,
    value: number,
    type: 'timing' | 'counter' | 'gauge' = 'gauge',
    tags?: Record<string, string>
  ) => {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: performance.now(),
      type,
      tags,
    };

    metricsBuffer.current.push(metric);
    setMetrics(current => [...current, metric].slice(-100));
  }, []);

  // Get current metrics
  const getMetrics = useCallback(() => {
    return [...metrics];
  }, [metrics]);

  // Get metrics buffer (all recorded metrics)
  const getMetricsBuffer = useCallback(() => {
    return [...metricsBuffer.current];
  }, []);

  // Clear metrics
  const clearMetrics = useCallback(() => {
    setMetrics([]);
    metricsBuffer.current = [];
  }, []);

  // Get browser performance timing data
  const getBrowserMetrics = useCallback(() => {
    const timing = performance.timing;
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

    if (!navigation) {
      return null;
    }

    return {
      // Navigation timing
      dns_lookup: navigation.domainLookupEnd - navigation.domainLookupStart,
      tcp_connection: navigation.connectEnd - navigation.connectStart,
      ssl_handshake: navigation.connectEnd - navigation.secureConnectionStart || 0,
      server_response: navigation.responseEnd - navigation.requestStart,
      dom_processing: navigation.domContentLoadedEventEnd - navigation.responseEnd,
      resource_loading: navigation.loadEventEnd - navigation.domContentLoadedEventEnd,
      total_load_time: navigation.loadEventEnd - navigation.navigationStart,

      // Page timing
      first_paint: 0,
      first_contentful_paint: 0,
      largest_contentful_paint: 0,
    };
  }, []);

  // Get memory usage (if available)
  const getMemoryMetrics = useCallback(() => {
    if ('memory' in performance) {
      const memory = (performance as any).memory;
      return {
        used_heap: memory.usedJSHeapSize,
        total_heap: memory.totalJSHeapSize,
        heap_limit: memory.jsHeapSizeLimit,
        heap_usage_ratio: memory.usedJSHeapSize / memory.totalJSHeapSize,
      };
    }
    return null;
  }, []);

  // Get resource timing data
  const getResourceMetrics = useCallback(() => {
    const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[];

    const metrics = {
      total_resources: resources.length,
      total_transfer_size: 0,
      total_encoded_size: 0,
      resource_types: {} as Record<string, number>,
      slow_resources: [] as Array<{name: string, duration: number}>,
    };

    resources.forEach(resource => {
      metrics.total_transfer_size += resource.transferSize || 0;
      metrics.total_encoded_size += resource.encodedBodySize || 0;

      // Count by type
      const type = resource.initiatorType || 'unknown';
      metrics.resource_types[type] = (metrics.resource_types[type] || 0) + 1;

      // Track slow resources (> 1 second)
      const duration = resource.responseEnd - resource.startTime;
      if (duration > 1000) {
        metrics.slow_resources.push({
          name: resource.name,
          duration,
        });
      }
    });

    return metrics;
  }, []);

  // Calculate performance score
  const getPerformanceScore = useCallback(() => {
    const browserMetrics = getBrowserMetrics();
    const memoryMetrics = getMemoryMetrics();
    const resourceMetrics = getResourceMetrics();

    if (!browserMetrics) {
      return null;
    }

    let score = 100;

    // Deduct points for slow load times
    if (browserMetrics.total_load_time > 3000) score -= 20;
    else if (browserMetrics.total_load_time > 2000) score -= 10;

    // Deduct points for slow FCP
    if (browserMetrics.first_contentful_paint > 2000) score -= 15;
    else if (browserMetrics.first_contentful_paint > 1000) score -= 5;

    // Deduct points for high memory usage
    if (memoryMetrics && memoryMetrics.heap_usage_ratio > 0.8) score -= 15;
    else if (memoryMetrics && memoryMetrics.heap_usage_ratio > 0.6) score -= 5;

    // Deduct points for many slow resources
    if (resourceMetrics && resourceMetrics.slow_resources.length > 5) score -= 10;
    else if (resourceMetrics && resourceMetrics.slow_resources.length > 2) score -= 5;

    return Math.max(0, score);
  }, [getBrowserMetrics, getMemoryMetrics, getResourceMetrics]);

  // Auto-collect browser metrics
  const collectBrowserMetrics = useCallback(() => {
    const browserMetrics = getBrowserMetrics();
    const memoryMetrics = getMemoryMetrics();
    const resourceMetrics = getResourceMetrics();

    if (browserMetrics) {
      Object.entries(browserMetrics).forEach(([key, value]) => {
        if (typeof value === 'number' && value > 0) {
          recordMetric(`browser.${key}`, value, 'timing');
        }
      });
    }

    if (memoryMetrics) {
      Object.entries(memoryMetrics).forEach(([key, value]) => {
        recordMetric(`memory.${key}`, value, 'gauge');
      });
    }

    if (resourceMetrics) {
      recordMetric('resources.total', resourceMetrics.total_resources, 'counter');
      recordMetric('resources.transfer_size', resourceMetrics.total_transfer_size, 'gauge');
      recordMetric('resources.slow_count', resourceMetrics.slow_resources.length, 'counter');
    }

    const performanceScore = getPerformanceScore();
    if (performanceScore !== null) {
      recordMetric('performance.score', performanceScore, 'gauge');
    }
  }, [getBrowserMetrics, getMemoryMetrics, getResourceMetrics, getPerformanceScore, recordMetric]);

  return {
    startMeasure,
    endMeasure,
    recordMetric,
    getMetrics,
    getMetricsBuffer,
    clearMetrics,
    getBrowserMetrics,
    getMemoryMetrics,
    getResourceMetrics,
    getPerformanceScore,
    collectBrowserMetrics,
  };
}
