/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        heading: ['"Baloo 2"', 'cursive'],
        body: ['"Comic Neue"', 'cursive'],
      },
      colors: {
        primary: '#4F46E5',
        secondary: '#818CF8',
        cta: '#22C55E',
        background: '#EEF2FF',
        text: '#312E81',
      },
      borderWidth: {
        '3': '3px',
      },
      animation: {
        'pulse': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
}
