/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'carbon': {
          950: '#0A0A0A',
          900: '#121212',
          800: '#1A1A1A',
          700: '#242424',
          600: '#2E2E2E',
        },
        'racing': {
          red: '#FF0040',
          orange: '#FF6B00',
          yellow: '#FFD700',
        },
        'metal': {
          chrome: '#E8E8E8',
          silver: '#C0C0C0',
          titanium: '#878681',
        },
        'neon': {
          blue: '#00D9FF',
          green: '#00FF88',
          purple: '#B026FF',
        }
      },
      fontFamily: {
        'display': ['Orbitron', 'system-ui', 'sans-serif'],
        'tech': ['Rajdhani', 'system-ui', 'sans-serif'],
        'body': ['Inter', 'system-ui', 'sans-serif'],
      },
      animation: {
        'scan': 'scan 2s ease-in-out infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-down': 'slideDown 0.5s ease-out',
        'fade-in': 'fadeIn 0.6s ease-out',
        'zoom-in': 'zoomIn 0.4s ease-out',
        'spin-slow': 'spin 8s linear infinite',
      },
      keyframes: {
        scan: {
          '0%, 100%': { transform: 'translateY(-100%)' },
          '50%': { transform: 'translateY(100%)' },
        },
        glow: {
          '0%': { boxShadow: '0 0 5px rgba(0, 217, 255, 0.5), 0 0 10px rgba(0, 217, 255, 0.3)' },
          '100%': { boxShadow: '0 0 20px rgba(0, 217, 255, 0.8), 0 0 30px rgba(0, 217, 255, 0.5)' },
        },
        slideUp: {
          '0%': { transform: 'translateY(20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-20px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        zoomIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
      backgroundImage: {
        'carbon-fiber': 'repeating-linear-gradient(45deg, #2a2a2a 0px, #2a2a2a 2px, #1a1a1a 2px, #1a1a1a 4px)',
        'metal-gradient': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        'racing-gradient': 'linear-gradient(135deg, #FF0040 0%, #FF6B00 100%)',
        'neon-gradient': 'linear-gradient(135deg, #00D9FF 0%, #B026FF 100%)',
      },
    },
  },
  plugins: [],
}