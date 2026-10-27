/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Color Schemes: Lemondrop (Light) & Glow (Dark)
        lemondrop: {
          bg: '#e8efe0',
          card: '#ffffff',
          cardAlt: '#f3f7ed',
          border: '#dfe7d6',
          borderLight: '#eef3e8',
          text: '#22261f',
          muted: '#5f6656',
          accent: '#7eaa3b',
          gold: '#c26700',
          highlight: 'rgba(242, 201, 76, 0.3)',
        },
        glow: {
          bg: '#161716',
          card: '#1e201d',
          cardAlt: '#232621',
          border: '#2f332b',
          borderLight: '#3a3f35',
          text: '#e6eae2',
          muted: '#989e92',
          neon: '#b8ee82',
          neonHover: '#c8f595',
          neonGlow: 'rgba(184, 238, 130, 0.25)',
          darkBar: '#101110',
        },
        vscode: {
          bg: '#161716',           // Glow main editor canvas
          sidebar: '#1a1c18',      // Glow sidebar
          panel: '#1e201d',        // Glow panels & cards
          header: '#252922',       // Glow table headers
          border: '#2f332b',       // Glow border
          borderLight: '#3a3f35',  // Glow secondary border
          hover: '#252922',        // Glow row hover
          active: '#2c3127',       // Glow active item
          input: '#252922',        // Glow input box
          blue: '#b8ee82',         // Glow neon accent
          blueHover: '#c8f595',
          blueActive: '#9cd663',
          text: '#e6eae2',         // Glow text
          textMuted: '#989e92',    // Glow muted text (WCAG AA compliant >= 4.5:1)
          textBright: '#ffffff',
          statusbar: '#161716',
        },
        aicte: {
          blue: '#002B49',
          orange: '#b86f00',
          navy: '#161716',
          gold: '#c26700',
        },
        // Direct mapping of Tailwind slate tokens in dark mode to Glow theme
        slate: {
          700: '#3a3f35',
          750: '#2f332b',
          800: '#252922',
          850: '#20231d',
          900: '#1e201d',
          950: '#161716',
        }
      },
      fontFamily: {
        sans: ['-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'sans-serif'],
        mono: ['Consolas', 'Menlo', 'Monaco', 'Courier New', 'monospace'],
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'elevated': '0 2px 4px 0 rgba(0, 0, 0, 0.15)',
        'none': 'none',
      }
    },
  },
  plugins: [],
}
