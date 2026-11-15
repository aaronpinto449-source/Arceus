/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{html,js,svelte,ts}",
  ],
  theme: {
    extend: {
      colors: {
        ares: {
          deep: '#080D16',       // Deep Space background
          navy: '#101A29',       // Mission Navy surfaces/panels
          elevated: '#172538',   // Elevated Navy cards/drawers
          cyan: '#36C5E8',       // Signal Cyan (active / navigation)
          ice: '#A5E8F5',        // Ice Blue (highlights / labels)
          amber: '#F2A93B',      // Alert Amber (warnings)
          red: '#EF5555',        // Critical Red (hazards)
          green: '#54C99A',      // Telemetry Green (nominal / verified)
          border: {
            subtle: '#142033',
            DEFAULT: '#1E2D42',
            bright: '#2A3E5B',
            cyan: 'rgba(54, 197, 232, 0.25)',
            amber: 'rgba(242, 169, 59, 0.25)',
            red: 'rgba(239, 85, 85, 0.25)',
            green: 'rgba(84, 201, 154, 0.25)',
          }
        },
        // Semantic compatibility mappings
        space: {
          950: '#080D16',
          900: '#101A29',
          850: '#142033',
          800: '#172538',
          750: '#1D2E45',
          700: '#243752',
          600: '#3A5274',
          border: '#1E2D42',
          'border-bright': '#2A3E5B',
        }
      },
      fontFamily: {
        title: ['"Space Grotesk"', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        'ares-sm': '2px',
        'ares': '4px',
        'ares-md': '6px',
        'ares-lg': '8px',
      },
      boxShadow: {
        'ares-panel': '0 4px 16px -2px rgba(0, 0, 0, 0.6), 0 0 1px 1px rgba(30, 45, 66, 0.4)',
        'ares-card': '0 2px 8px -1px rgba(0, 0, 0, 0.5), 0 0 1px 1px rgba(20, 32, 51, 0.6)',
        'ares-glow-cyan': '0 0 12px -2px rgba(54, 197, 232, 0.3)',
        'ares-glow-amber': '0 0 12px -2px rgba(242, 169, 59, 0.3)',
        'ares-glow-red': '0 0 12px -2px rgba(239, 85, 85, 0.3)',
        'ares-glow-green': '0 0 12px -2px rgba(84, 201, 154, 0.3)',
      }
    },
  },
  plugins: [],
}
