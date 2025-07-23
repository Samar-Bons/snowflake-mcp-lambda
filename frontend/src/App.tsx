// ABOUTME: Main App component with routing and theme management
// ABOUTME: Provides authentication context and manages global app state

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import { LandingPage } from './pages/LandingPage';
import { ChatPage } from './pages/ChatPage';
import { useEffect, useState } from 'react';

function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    // Apply theme to document
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update Tailwind dark mode class
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => prevTheme === 'dark' ? 'light' : 'dark');
  };

  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-primary text-light-primary">
          <Routes>
            <Route 
              path="/" 
              element={
                <LandingPage 
                  theme={theme} 
                  onToggleTheme={toggleTheme} 
                />
              } 
            />
            <Route 
              path="/chat" 
              element={
                <ChatPage 
                  theme={theme} 
                  onToggleTheme={toggleTheme} 
                />
              } 
            />
            <Route 
              path="/chat/:fileId" 
              element={
                <ChatPage 
                  theme={theme} 
                  onToggleTheme={toggleTheme} 
                />
              } 
            />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;