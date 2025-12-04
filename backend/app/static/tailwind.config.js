/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../templates/**/*.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: {
          indigo: '#1C1A3F',
          cocoa: '#6E4A31',
        },
        accent: {
          sky: '#9BCFF1',
          rose: '#E9B8D8',
          gold: '#F4C85C',
        },
        support: {
          teal: '#2A6F6B',
        },
        neutral: {
          ivory: '#F7F5F2',
          charcoal: '#2F2F2F',
        },
      },
    },
  },
  plugins: [],
}
