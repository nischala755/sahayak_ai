/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Custom SAHAYAK AI color palette
                primary: {
                    50: '#e3f2fd',
                    100: '#bbdefb',
                    200: '#90caf9',
                    300: '#64b5f6',
                    400: '#42a5f5',
                    500: '#1976d2',
                    600: '#1565c0',
                    700: '#0d47a1',
                    800: '#0a3d91',
                    900: '#082f6e',
                },
                secondary: {
                    50: '#e8f5e9',
                    100: '#c8e6c9',
                    200: '#a5d6a7',
                    300: '#81c784',
                    400: '#66bb6a',
                    500: '#43a047',
                    600: '#388e3c',
                    700: '#2e7d32',
                    800: '#256028',
                    900: '#1b5e20',
                },
                accent: {
                    50: '#fff3e0',
                    100: '#ffe0b2',
                    200: '#ffcc80',
                    300: '#ffb74d',
                    400: '#ffa726',
                    500: '#ff9800',
                    600: '#fb8c00',
                    700: '#f57c00',
                    800: '#ef6c00',
                    900: '#e65100',
                },
                danger: {
                    500: '#ef4444',
                    600: '#dc2626',
                },
                dark: {
                    100: '#1e293b',
                    200: '#0f172a',
                    300: '#020617',
                }
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'float': 'float 3s ease-in-out infinite',
                'glow': 'glow 2s ease-in-out infinite alternate',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0)' },
                    '50%': { transform: 'translateY(-10px)' },
                },
                glow: {
                    '0%': { boxShadow: '0 0 5px #1976d2, 0 0 10px #1976d2' },
                    '100%': { boxShadow: '0 0 20px #1976d2, 0 0 30px #1976d2' },
                }
            },
            backgroundImage: {
                'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
                'hero-pattern': 'linear-gradient(135deg, #1976d2 0%, #0d47a1 50%, #082f6e 100%)',
            }
        },
    },
    plugins: [],
}
