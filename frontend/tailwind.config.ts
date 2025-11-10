import type { Config } from 'tailwindcss'

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#4F46E5',
          900: '#312E81',
        },
        accent: {
          DEFAULT: '#FF6B6B',
          50: '#FFE3E3',
        },
        ink: {
          DEFAULT: '#0B1020',
          30: 'rgba(11, 16, 32, 0.3)',
          50: 'rgba(11, 16, 32, 0.5)',
          70: 'rgba(11, 16, 32, 0.7)',
          80: 'rgba(11, 16, 32, 0.8)',
          90: 'rgba(11, 16, 32, 0.9)',
        },
        'panel-dark': '#111827',
        paper: '#F8FAFC',
        'panel-light': '#E5E7EB',
        muted: '#9CA3AF',
        success: '#22C55E',
        warning: '#F59E0B',
        error: '#EF4444',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
} satisfies Config

