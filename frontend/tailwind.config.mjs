/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // shadcn/ui CSS variables
        background: 'hsl(var(--background))',
        foreground: 'hsl(var(--foreground))',
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))'
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))'
        },
        primary: {
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
          // 保留原有的海浪泡沫配色
          50: '#F5FFFA',    // 薄荷白
          100: '#D9F1FA',   // 浅天蓝
          200: '#CDDDFA',   // 点缀背景
          300: '#93A5ED',   // 主色
          400: '#93A5ED',   // 主色
          500: '#93A5ED',   // 主色
          600: '#7A8ED9',   // 主色深一点
          700: '#6277C5',   // 主色更深
          800: '#4A60B0',   // 主色暗色
          900: '#32499C',   // 主色最深
        },
        secondary: {
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
          // 保留原有的辅助色
          50: '#F0F5F4',    // 辅助色超浅
          100: '#E0ECEB',   // 辅助色浅
          200: '#D0E3E2',   // 辅助色较浅
          300: '#9FBFBC',   // 辅助色
          400: '#9FBFBC',   // 辅助色
          500: '#9FBFBC',   // 辅助色
          600: '#7FA8A5',   // 辅助色深一点
          700: '#5F918E',   // 辅助色更深
          800: '#3F7A77',   // 辅助色暗色
          900: '#1F6360',   // 辅助色最深
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))'
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))'
        },
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))'
        },
        border: 'hsl(var(--border))',
        input: 'hsl(var(--input))',
        ring: 'hsl(var(--ring))',
        chart: {
          '1': 'hsl(var(--chart-1))',
          '2': 'hsl(var(--chart-2))',
          '3': 'hsl(var(--chart-3))',
          '4': 'hsl(var(--chart-4))',
          '5': 'hsl(var(--chart-5))'
        },
        // 保留自定义配色
        custom: {
          white: '#FFFFFF',
          lightest: '#F5FFFA',    // 薄荷白背景
          light: '#D9F1FA',        // 浅天蓝背景
          accent: '#CDDDFA',       // 点缀背景
          medium: '#9FBFBC',       // 辅助色
          dark: '#93A5ED',         // 主色
        },
        // 保留原有的背景色
        'background-mint': '#F5FFFA',
        success: '#28A745',
        danger: '#DC3545',
        warning: '#FFC107',
      },
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)'
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
}