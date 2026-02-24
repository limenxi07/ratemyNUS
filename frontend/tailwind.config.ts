import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Semantic color names (role-based)
        background: '#EDF2FB',
        navbar: '#E2EAFC',
        'outline-primary': '#C1D3FE',
        'outline-active': '#ABC4FF',
        'text-primary': '#5C8DFF',
        'text-body': '#2B2D2F',
        'surface': '#FDFCF8',
        'peach': '#F7B4B4', // error colour
      },
      fontFamily: {
        serif: ['Instrument Serif', 'Lora', 'Georgia', 'serif'],
        sans: ['PT Serif', 'system-ui', 'sans-serif'], // changed to serif but retained name
      },
      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
      }
    },
  },
  plugins: [],
};
export default config;