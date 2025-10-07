/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // 海浪泡沫配色方案
        primary: {
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
        custom: {
          white: '#FFFFFF',
          lightest: '#F5FFFA',    // 薄荷白背景
          light: '#D9F1FA',        // 浅天蓝背景
          accent: '#CDDDFA',       // 点缀背景
          medium: '#9FBFBC',       // 辅助色
          dark: '#93A5ED',         // 主色
        },
        background: {
          primary: '#FFFFFF',      // 纯白背景
          secondary: '#F8F9FA',    // 极浅灰色背景
          light: '#D9F1FA',        // 浅天蓝背景
          accent: '#CDDDFA',       // 点缀背景
          mint: '#F5FFFA',         // 薄荷白背景
        },
        text: {
          primary: '#212529',      // 主要文本（深灰）
          secondary: '#6C757D',    // 次要文本（中灰）
        },
        border: {
          light: '#E9ECEF',        // 浅灰边框
        },
        success: '#28A745',        // 成功状态
        danger: '#DC3545',         // 危险/错误状态
        warning: '#FFC107',        // 警告状态
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