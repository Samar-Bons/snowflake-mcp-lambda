// ABOUTME: Login page component with Google OAuth integration
// ABOUTME: Provides authentication entry point for the application

import { Navigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { LoginButton } from '../components/auth/LoginButton';
import { Card } from '../components/ui/Card';

export function LoginPage() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-slate-400">Loading...</p>
        </div>
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/app" replace />;
  }

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Snowflake Chat</h1>
          <p className="text-slate-400">
            Connect to your Snowflake database and query with natural language
          </p>
        </div>

        <Card>
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100 mb-2">
                Welcome back
              </h2>
              <p className="text-slate-600 dark:text-slate-400">
                Sign in to continue to your dashboard
              </p>
            </div>

            <LoginButton />

            <div className="text-xs text-slate-500 dark:text-slate-400 text-center">
              By signing in, you agree to our terms of service and privacy policy.
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
