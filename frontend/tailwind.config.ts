import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#1A56DB', // brand primary
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
        risk: {
          high: '#E02424',
          'high-bg': '#FDF2F2',
          medium: '#D97706',
          'medium-bg': '#FFFBEB',
          low: '#057A55',
          'low-bg': '#F3FAF7',
        },
      },
      borderRadius: {
        DEFAULT: '0.5rem',
      },
    },
  },
  plugins: [],
};

export default config;
