/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'arduino': '#00979D',
        'masumi': '#6366f1',
        'sokosumi': '#8b5cf6',
      }
    },
  },
  plugins: [],
}