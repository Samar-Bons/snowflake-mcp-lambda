// ABOUTME: Tailwind CSS configuration with custom design system integration
// ABOUTME: Imports and extends the professional dark theme from styleGuide directory

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: ['class', '[data-theme="dark"]'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        // Primary theme colors (from design system)
        primary: {
          dark: '#0a0a0a',
          DEFAULT: '#0a0a0a',
        },
        secondary: {
          dark: '#1a1a1a',
          DEFAULT: '#1a1a1a',
        },
        surface: {
          DEFAULT: '#2a2a2a',
          elevated: '#353535',
        },
        // Blue accent colors (Tailwind 400/600 scale)
        blue: {
          primary: '#60a5fa',
          secondary: '#2563eb',
          light: '#93c5fd',
        },
        // Purple accent colors
        purple: {
          primary: '#a78bfa',
          secondary: '#9333ea',
          light: '#c4b5fd',
        },
        // Light colors for text
        light: {
          primary: '#f8fafc',
          secondary: '#e2e8f0',
          muted: '#94a3b8',
          subtle: '#64748b',
        },
        // Semantic colors
        success: '#10b981',
        warning: '#f59e0b',
        error: '#ef4444',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
      borderRadius: {
        'xl': '1rem',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(96, 165, 250, 0.3)',
        'glow-purple': '0 0 20px rgba(167, 139, 250, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'typing': 'typing 1.4s infinite ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        typing: {
          '0%, 60%, 100%': { opacity: '0.3', transform: 'translateY(0)' },
          '30%': { opacity: '1', transform: 'translateY(-4px)' },
        },
      },
    },
  },
  plugins: [],
}
