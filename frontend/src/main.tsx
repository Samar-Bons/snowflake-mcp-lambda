// ABOUTME: React application entry point with strict mode and CSS imports
// ABOUTME: Mounts the main App component to the DOM root element

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)