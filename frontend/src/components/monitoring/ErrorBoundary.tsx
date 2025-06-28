// ABOUTME: React Error Boundary component for catching and logging frontend errors
// ABOUTME: Provides fallback UI and automatic error reporting to monitoring system

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { MonitoringService } from '../../services/monitoring';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorId?: string;
}

export class ErrorBoundary extends Component<Props, State> {
  private monitoringService: MonitoringService;

  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
    this.monitoringService = new MonitoringService();
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorId: crypto.randomUUID(),
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log error to monitoring service
    this.monitoringService.reportError({
      error,
      errorInfo,
      errorId: this.state.errorId!,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: this.getUserId(),
      component: 'ErrorBoundary',
      stackTrace: error.stack,
      componentStack: errorInfo.componentStack,
    });

    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log to console for development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error caught by ErrorBoundary:', error);
      console.error('Component stack:', errorInfo.componentStack);
    }
  }

  private getUserId(): string | undefined {
    // Get user ID from context or localStorage
    return localStorage.getItem('userId') || undefined;
  }

  private handleRetry = (): void => {
    this.setState({ hasError: false, error: undefined, errorId: undefined });
  };

  private handleReportIssue = (): void => {
    // Open issue reporting interface
    const { error, errorId } = this.state;
    if (error && errorId) {
      // You could integrate with issue tracking system here
      const issueData = {
        errorId,
        message: error.message,
        timestamp: new Date().toISOString(),
        url: window.location.href,
      };

      // For now, copy to clipboard
      navigator.clipboard.writeText(JSON.stringify(issueData, null, 2))
        .then(() => alert('Error details copied to clipboard'))
        .catch(() => console.error('Failed to copy error details'));
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="error-boundary">
          <div className="error-boundary__container">
            <div className="error-boundary__icon">⚠️</div>
            <h2 className="error-boundary__title">Something went wrong</h2>
            <p className="error-boundary__message">
              We're sorry, but something unexpected happened. The error has been
              reported automatically.
            </p>

            {process.env.NODE_ENV === 'development' && (
              <details className="error-boundary__details">
                <summary>Error Details (Development)</summary>
                <pre className="error-boundary__error">
                  {this.state.error?.message}
                  {'\n\n'}
                  {this.state.error?.stack}
                </pre>
              </details>
            )}

            <div className="error-boundary__actions">
              <button
                onClick={this.handleRetry}
                className="error-boundary__button error-boundary__button--primary"
              >
                Try Again
              </button>
              <button
                onClick={this.handleReportIssue}
                className="error-boundary__button error-boundary__button--secondary"
              >
                Report Issue
              </button>
              <button
                onClick={() => window.location.reload()}
                className="error-boundary__button error-boundary__button--secondary"
              >
                Reload Page
              </button>
            </div>

            {this.state.errorId && (
              <p className="error-boundary__error-id">
                Error ID: {this.state.errorId}
              </p>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// Higher-order component for wrapping components with error boundary
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  fallback?: ReactNode
) {
  const ComponentWithErrorBoundary = (props: P) => (
    <ErrorBoundary fallback={fallback}>
      <WrappedComponent {...props} />
    </ErrorBoundary>
  );

  ComponentWithErrorBoundary.displayName =
    `withErrorBoundary(${WrappedComponent.displayName || WrappedComponent.name})`;

  return ComponentWithErrorBoundary;
}

// Hook for manual error reporting
export function useErrorReporting() {
  const monitoringService = React.useMemo(() => new MonitoringService(), []);

  const reportError = React.useCallback((error: Error, context?: Record<string, any>) => {
    monitoringService.reportError({
      error,
      errorId: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      userId: localStorage.getItem('userId') || undefined,
      component: 'Manual',
      stackTrace: error.stack,
      context,
    });
  }, [monitoringService]);

  return { reportError };
}
