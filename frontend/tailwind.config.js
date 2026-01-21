/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        // Polymarket color palette
        'pm-bg-primary': '#0a0a0a',
        'pm-bg-secondary': '#141414',
        'pm-bg-card': '#1a1a1a',
        'pm-text-primary': '#ffffff',
        'pm-text-secondary': '#a0a0a0',
        'pm-border': '#2a2a2a',
        'pm-green': '#00d4aa',
        'pm-green-dark': '#00b894',
        'pm-red': '#ff6b6b',
        'pm-red-dark': '#ee5a5a',
        'pm-blue': '#4dabf7',
        'pm-yellow': '#ffd43b',
      },
      fontFamily: {
        sans: [
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Oxygen',
          'Ubuntu',
          'Cantarell',
          'Fira Sans',
          'Droid Sans',
          'Helvetica Neue',
          'sans-serif',
        ],
      },
    },
  },
  plugins: [],
}








