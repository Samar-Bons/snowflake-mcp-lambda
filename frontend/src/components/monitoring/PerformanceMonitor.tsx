// ABOUTME: Performance monitoring component for tracking frontend metrics
// ABOUTME: Monitors page load times, component render performance, and user interactions

import React, { useEffect, useRef, useState } from 'react';
import { MonitoringService } from '../../services/monitoring';
import { usePerformanceMetrics } from '../../hooks/usePerformanceMetrics';

interface PerformanceMonitorProps {
  enabled?: boolean;
  sampleRate?: number; // 0-1, percentage of sessions to monitor
  children: React.ReactNode;
}

interface PerformanceData {
  renderTime: number;
  componentName: string;
  timestamp: string;
  props?: Record<string, any>;
}

export const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  enabled = true,
  sampleRate = 1.0,
  children,
}) => {
  const monitoringService = useRef(new MonitoringService());
  const [isMonitoring, setIsMonitoring] = useState(false);
  const { startMeasure, endMeasure, getMetrics } = usePerformanceMetrics();

  // Determine if this session should be monitored
  useEffect(() => {
    if (enabled && Math.random() < sampleRate) {
      setIsMonitoring(true);
    }
  }, [enabled, sampleRate]);

  // Monitor initial page load performance
  useEffect(() => {
    if (!isMonitoring) return;

    const measurePageLoad = () => {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;

      if (navigation) {
        const loadMetrics = {
          dns_lookup: navigation.domainLookupEnd - navigation.domainLookupStart,
          tcp_connection: navigation.connectEnd - navigation.connectStart,
          server_response: navigation.responseEnd - navigation.requestStart,
          dom_processing: navigation.domContentLoadedEventEnd - navigation.responseEnd,
          page_load_total: navigation.loadEventEnd - navigation.navigationStart,
          first_contentful_paint: 0,
          largest_contentful_paint: 0,
        };

        // Get paint metrics
        const paintEntries = performance.getEntriesByType('paint');
        paintEntries.forEach((entry) => {
          if (entry.name === 'first-contentful-paint') {
            loadMetrics.first_contentful_paint = entry.startTime;
          }
        });

        // Get LCP
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          loadMetrics.largest_contentful_paint = lastEntry.startTime;

          monitoringService.current.reportPerformanceMetrics({
            type: 'page_load',
            metrics: loadMetrics,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userId: localStorage.getItem('userId') || undefined,
          });
        });

        observer.observe({ entryTypes: ['largest-contentful-paint'] });

        // Cleanup observer after 10 seconds
        setTimeout(() => observer.disconnect(), 10000);
      }
    };

    // Wait for page to fully load
    if (document.readyState === 'complete') {
      measurePageLoad();
    } else {
      window.addEventListener('load', measurePageLoad);
      return () => window.removeEventListener('load', measurePageLoad);
    }
  }, [isMonitoring]);

  // Monitor memory usage
  useEffect(() => {
    if (!isMonitoring) return;

    const monitorMemory = () => {
      if ('memory' in performance) {
        const memoryInfo = (performance as any).memory;

        monitoringService.current.reportPerformanceMetrics({
          type: 'memory_usage',
          metrics: {
            used_heap: memoryInfo.usedJSHeapSize,
            total_heap: memoryInfo.totalJSHeapSize,
            heap_limit: memoryInfo.jsHeapSizeLimit,
          },
          timestamp: new Date().toISOString(),
          url: window.location.href,
          userId: localStorage.getItem('userId') || undefined,
        });
      }
    };

    const interval = setInterval(monitorMemory, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, [isMonitoring]);

  if (!isMonitoring) {
    return <>{children}</>;
  }

  return <>{children}</>;
};

// HOC for monitoring component performance
export function withPerformanceMonitoring<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  componentName?: string
) {
  const ComponentWithPerformance = React.forwardRef<any, P>((props, ref) => {
    const monitoringService = useRef(new MonitoringService());
    const renderStartTime = useRef<number>();
    const mountTime = useRef<number>();

    const name = componentName || WrappedComponent.displayName || WrappedComponent.name;

    // Measure mount time
    useEffect(() => {
      const mountEnd = performance.now();
      if (mountTime.current) {
        const mountDuration = mountEnd - mountTime.current;

        monitoringService.current.reportPerformanceMetrics({
          type: 'component_mount',
          metrics: {
            component_name: name,
            mount_time_ms: mountDuration,
          },
          timestamp: new Date().toISOString(),
          url: window.location.href,
          userId: localStorage.getItem('userId') || undefined,
        });
      }
    }, []);

    // Measure render time
    const measureRender = () => {
      renderStartTime.current = performance.now();
    };

    useEffect(() => {
      if (renderStartTime.current) {
        const renderEnd = performance.now();
        const renderDuration = renderEnd - renderStartTime.current;

        // Only report slow renders (> 16ms for 60fps)
        if (renderDuration > 16) {
          monitoringService.current.reportPerformanceMetrics({
            type: 'component_render',
            metrics: {
              component_name: name,
              render_time_ms: renderDuration,
              is_slow_render: renderDuration > 100,
            },
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userId: localStorage.getItem('userId') || undefined,
          });
        }
      }
    });

    // Track mount start time
    mountTime.current = performance.now();
    measureRender();

    return <WrappedComponent {...props} ref={ref} />;
  });

  ComponentWithPerformance.displayName = `withPerformanceMonitoring(${name})`;
  return ComponentWithPerformance;
}

// Component for displaying performance metrics (development/admin use)
export const PerformanceDisplay: React.FC = () => {
  const [metrics, setMetrics] = useState<any[]>([]);
  const { getMetrics } = usePerformanceMetrics();

  useEffect(() => {
    const updateMetrics = () => {
      const currentMetrics = getMetrics();
      setMetrics(currentMetrics);
    };

    const interval = setInterval(updateMetrics, 1000);
    updateMetrics();

    return () => clearInterval(interval);
  }, [getMetrics]);

  if (process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="performance-display">
      <h3>Performance Metrics</h3>
      <div className="performance-metrics">
        {metrics.map((metric, index) => (
          <div key={index} className="metric-item">
            <span className="metric-name">{metric.name}</span>
            <span className="metric-value">{metric.value.toFixed(2)}ms</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Hook for manual performance measurements
export function usePerformanceTracking() {
  const monitoringService = useRef(new MonitoringService());

  const trackOperation = React.useCallback((operationName: string) => {
    const startTime = performance.now();

    return {
      finish: (metadata?: Record<string, any>) => {
        const duration = performance.now() - startTime;

        monitoringService.current.reportPerformanceMetrics({
          type: 'user_operation',
          metrics: {
            operation_name: operationName,
            duration_ms: duration,
            ...metadata,
          },
          timestamp: new Date().toISOString(),
          url: window.location.href,
          userId: localStorage.getItem('userId') || undefined,
        });

        return duration;
      }
    };
  }, []);

  const trackInteraction = React.useCallback((
    interactionType: string,
    targetElement?: string,
    metadata?: Record<string, any>
  ) => {
    monitoringService.current.reportUserInteraction({
      type: interactionType,
      target: targetElement,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userId: localStorage.getItem('userId') || undefined,
      metadata,
    });
  }, []);

  return {
    trackOperation,
    trackInteraction,
  };
}
