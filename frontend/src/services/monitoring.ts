// ABOUTME: Frontend monitoring service for error tracking and performance reporting
// ABOUTME: Handles communication with backend monitoring system and external services

import { ErrorInfo } from 'react';

interface ErrorReport {
  error: Error;
  errorInfo?: ErrorInfo;
  errorId: string;
  timestamp: string;
  userAgent: string;
  url: string;
  userId?: string;
  component: string;
  stackTrace?: string;
  componentStack?: string;
  context?: Record<string, any>;
}

interface PerformanceReport {
  type: string;
  metrics: Record<string, any>;
  timestamp: string;
  url: string;
  userId?: string;
  sessionId?: string;
}

interface UserInteractionReport {
  type: string;
  target?: string;
  timestamp: string;
  url: string;
  userId?: string;
  metadata?: Record<string, any>;
}

interface MonitoringConfig {
  apiEndpoint: string;
  apiKey?: string;
  enabled: boolean;
  sampleRate: number;
  bufferSize: number;
  flushInterval: number; // milliseconds
}

export class MonitoringService {
  private config: MonitoringConfig;
  private errorBuffer: ErrorReport[] = [];
  private performanceBuffer: PerformanceReport[] = [];
  private interactionBuffer: UserInteractionReport[] = [];
  private flushTimer: NodeJS.Timeout | null = null;
  private sessionId: string;

  constructor(config?: Partial<MonitoringConfig>) {
    this.config = {
      apiEndpoint: '/api/monitoring',
      enabled: true,
      sampleRate: 1.0,
      bufferSize: 100,
      flushInterval: 30000, // 30 seconds
      ...config,
    };

    this.sessionId = this.generateSessionId();
    this.startFlushTimer();
    this.setupBeforeUnloadHandler();
  }

  private generateSessionId(): string {
    return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private startFlushTimer(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }

    this.flushTimer = setInterval(() => {
      this.flush();
    }, this.config.flushInterval);
  }

  private setupBeforeUnloadHandler(): void {
    window.addEventListener('beforeunload', () => {
      // Flush remaining data before page unload
      this.flush(true);
    });
  }

  // Report JavaScript errors
  reportError(errorReport: ErrorReport): void {
    if (!this.config.enabled || !this.shouldSample()) {
      return;
    }

    // Add session ID
    const enrichedReport = {
      ...errorReport,
      sessionId: this.sessionId,
      breadcrumbs: this.getBreadcrumbs(),
    };

    this.errorBuffer.push(enrichedReport);

    // Immediately flush critical errors
    if (errorReport.error.name === 'ChunkLoadError' ||
        errorReport.error.message.includes('Loading chunk')) {
      this.flush();
    }

    // Flush buffer if it's getting full
    if (this.errorBuffer.length >= this.config.bufferSize) {
      this.flush();
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Frontend Error Reported:', errorReport);
    }
  }

  // Report performance metrics
  reportPerformanceMetrics(performanceReport: PerformanceReport): void {
    if (!this.config.enabled || !this.shouldSample()) {
      return;
    }

    const enrichedReport = {
      ...performanceReport,
      sessionId: this.sessionId,
    };

    this.performanceBuffer.push(enrichedReport);

    // Flush if buffer is full
    if (this.performanceBuffer.length >= this.config.bufferSize) {
      this.flush();
    }
  }

  // Report user interactions
  reportUserInteraction(interactionReport: UserInteractionReport): void {
    if (!this.config.enabled || !this.shouldSample()) {
      return;
    }

    const enrichedReport = {
      ...interactionReport,
      sessionId: this.sessionId,
    };

    this.interactionBuffer.push(enrichedReport);

    // Add to breadcrumbs
    this.addBreadcrumb({
      type: 'user_interaction',
      data: interactionReport,
      timestamp: interactionReport.timestamp,
    });

    // Flush if buffer is full
    if (this.interactionBuffer.length >= this.config.bufferSize) {
      this.flush();
    }
  }

  // Check if we should sample this event
  private shouldSample(): boolean {
    return Math.random() < this.config.sampleRate;
  }

  // Flush all buffers to backend
  private async flush(sync: boolean = false): Promise<void> {
    const errors = [...this.errorBuffer];
    const performance = [...this.performanceBuffer];
    const interactions = [...this.interactionBuffer];

    // Clear buffers
    this.errorBuffer = [];
    this.performanceBuffer = [];
    this.interactionBuffer = [];

    if (errors.length === 0 && performance.length === 0 && interactions.length === 0) {
      return;
    }

    const payload = {
      sessionId: this.sessionId,
      timestamp: new Date().toISOString(),
      errors,
      performance,
      interactions,
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: localStorage.getItem('userId') || undefined,
    };

    try {
      if (sync && navigator.sendBeacon) {
        // Use sendBeacon for synchronous sending (page unload)
        navigator.sendBeacon(
          this.config.apiEndpoint,
          JSON.stringify(payload)
        );
      } else {
        // Regular async request
        await fetch(this.config.apiEndpoint, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(this.config.apiKey && { 'Authorization': `Bearer ${this.config.apiKey}` }),
          },
          body: JSON.stringify(payload),
          keepalive: sync,
        });
      }
    } catch (error) {
      // Don't throw - monitoring shouldn't break the app
      console.warn('Failed to send monitoring data:', error);

      // If the request failed, put the data back in buffers (up to limit)
      if (!sync) {
        this.errorBuffer.unshift(...errors.slice(-50));
        this.performanceBuffer.unshift(...performance.slice(-50));
        this.interactionBuffer.unshift(...interactions.slice(-50));
      }
    }
  }

  // Breadcrumb management for error context
  private breadcrumbs: Array<{
    type: string;
    data: any;
    timestamp: string;
  }> = [];

  private addBreadcrumb(breadcrumb: { type: string; data: any; timestamp: string }): void {
    this.breadcrumbs.push(breadcrumb);

    // Keep only last 20 breadcrumbs
    if (this.breadcrumbs.length > 20) {
      this.breadcrumbs = this.breadcrumbs.slice(-20);
    }
  }

  private getBreadcrumbs(): Array<{ type: string; data: any; timestamp: string }> {
    return [...this.breadcrumbs];
  }

  // Manual breadcrumb addition
  addBreadcrumbManual(type: string, data: any): void {
    this.addBreadcrumb({
      type,
      data,
      timestamp: new Date().toISOString(),
    });
  }

  // Update configuration
  updateConfig(newConfig: Partial<MonitoringConfig>): void {
    this.config = { ...this.config, ...newConfig };

    if (newConfig.flushInterval) {
      this.startFlushTimer();
    }
  }

  // Manually flush data
  async flushNow(): Promise<void> {
    await this.flush();
  }

  // Get current buffer sizes (for debugging)
  getBufferSizes(): { errors: number; performance: number; interactions: number } {
    return {
      errors: this.errorBuffer.length,
      performance: this.performanceBuffer.length,
      interactions: this.interactionBuffer.length,
    };
  }

  // Cleanup
  destroy(): void {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
      this.flushTimer = null;
    }

    // Final flush
    this.flush(true);
  }
}

// Global monitoring instance
let globalMonitoringService: MonitoringService | null = null;

export function initializeMonitoring(config?: Partial<MonitoringConfig>): MonitoringService {
  if (globalMonitoringService) {
    globalMonitoringService.destroy();
  }

  globalMonitoringService = new MonitoringService(config);

  // Set up global error handlers
  window.addEventListener('error', (event) => {
    globalMonitoringService?.reportError({
      error: new Error(event.message),
      errorId: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: localStorage.getItem('userId') || undefined,
      component: 'GlobalErrorHandler',
      stackTrace: event.error?.stack,
      context: {
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno,
      },
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    globalMonitoringService?.reportError({
      error: new Error(`Unhandled Promise Rejection: ${event.reason}`),
      errorId: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: localStorage.getItem('userId') || undefined,
      component: 'GlobalPromiseRejectionHandler',
      stackTrace: event.reason?.stack,
    });
  });

  return globalMonitoringService;
}

export function getMonitoringService(): MonitoringService | null {
  return globalMonitoringService;
}

// React DevTools profiler integration
export function createProfilerOnRender(componentName: string) {
  return (
    id: string,
    phase: 'mount' | 'update',
    actualDuration: number,
    baseDuration: number,
    startTime: number,
    commitTime: number
  ) => {
    if (globalMonitoringService && actualDuration > 16) { // Only report slow renders
      globalMonitoringService.reportPerformanceMetrics({
        type: 'react_profiler',
        metrics: {
          component_name: componentName,
          id,
          phase,
          actual_duration: actualDuration,
          base_duration: baseDuration,
          start_time: startTime,
          commit_time: commitTime,
        },
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userId: localStorage.getItem('userId') || undefined,
      });
    }
  };
}
