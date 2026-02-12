/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'mh-black': '#0F0F0F',
                'mh-gray': '#1A1A1A',
                'mh-red': '#FF4500',
                'mh-gold': '#D4AF37',
                'mh-blue': '#4A90E2',
            },
            fontFamily: {
                'os': ['Consolas', 'Menlo', 'Courier New', 'monospace'],
                'sans': ['Outfit', 'Noto Sans KR', 'sans-serif'],
            },
            animation: {
                'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
            }
        },
    },
    plugins: [],
}
