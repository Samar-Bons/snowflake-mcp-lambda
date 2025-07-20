// ABOUTME: Google OAuth login button component
// ABOUTME: Triggers authentication flow with backend OAuth endpoint

import { useState } from 'react';
import { Button } from '../ui/Button';
import { useAuth } from '../../hooks/useAuth';
import { GoogleIcon } from '../icons';

export function LoginButton() {
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    try {
      setIsLoading(true);
      await login();
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoading(false);
    }
  };

  return (
    <Button
      onClick={handleLogin}
      isLoading={isLoading}
      size="lg"
      className="w-full"
    >
      <GoogleIcon className="w-5 h-5 mr-2" />
      Continue with Google
    </Button>
  );
}
