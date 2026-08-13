import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        violet: {
          DEFAULT: '#6F13EE',
          dark: '#340873',
        },
        cyan: {
          DEFAULT: '#63E0BF',
        },
        orange: {
          DEFAULT: '#ED785D',
        },
        ink: '#12081F',
        paper: '#FBFAFD',
      },
      fontFamily: {
        display: ['"Big Shoulders Display"', 'system-ui', 'sans-serif'],
        body: ['Montserrat', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '1rem',
      },
      boxShadow: {
        // Ombres violettes, jamais de gris neutre.
        violet: '0 12px 40px -12px rgba(111,19,238,0.35)',
        'violet-lg': '0 24px 60px -16px rgba(111,19,238,0.45)',
        'violet-sm': '0 6px 20px -8px rgba(111,19,238,0.30)',
      },
      maxWidth: {
        container: '1280px',
      },
      keyframes: {
        'fade-in': {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
      },
      transitionTimingFunction: {
        spring: 'cubic-bezier(0.22, 1, 0.36, 1)',
      },
    },
  },
  plugins: [],
} satisfies Config;
