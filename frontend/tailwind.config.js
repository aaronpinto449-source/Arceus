/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        space: {
          950: '#06080d',
          900: '#090d14',
          850: '#0d131d',
          800: '#111827',
          750: '#172030',
          700: '#1e293b',
          600: '#334155',
          border: '#1f2b3e',
          'border-bright': '#2e415e',
        },
        ares: {
          cyan: '#00f0ff',
          'cyan-dim': 'rgba(0, 240, 255, 0.15)',
          green: '#54d69a',
          'green-dim': 'rgba(84, 214, 154, 0.15)',
          amber: '#f59e0b',
          'amber-dim': 'rgba(245, 158, 11, 0.15)',
          coral: '#e16d49',
          'coral-dim': 'rgba(225, 109, 73, 0.18)',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      }
    },
  },
  plugins: [],
}

