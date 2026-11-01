/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sidebar:   '#0F172A',
        accent:    '#38BDF8',
        'accent-dark': '#0EA5E9',
        success:   '#10B981',
        danger:    '#EF4444',
        warning:   '#F59E0B',
        'bg-main': '#F1F5F9',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 1px 3px 0 rgba(0,0,0,0.06), 0 1px 2px -1px rgba(0,0,0,0.04)',
        'card-hover': '0 4px 12px 0 rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.04)',
        'sidebar': '4px 0 24px 0 rgba(0,0,0,0.15)',
      },
      borderRadius: {
        'xl2': '1rem',
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      animation: {
        'fade-up': 'fadeUp 0.25s ease-out',
        'shimmer': 'shimmer 1.5s linear infinite',
      },
    },
  },
  plugins: [],
}
