import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useThemeStore = defineStore('theme', () => {
  const isDark = ref(false);
  
  const initTheme = () => {
    if (typeof window === 'undefined') return;
    
    const saved = localStorage.getItem('theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    isDark.value = saved === 'dark' || (!saved && prefersDark);
    applyTheme();
  };
  
  const toggleTheme = () => {
    isDark.value = !isDark.value;
    applyTheme();
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
    }
  };
  
  const applyTheme = () => {
    if (typeof document !== 'undefined') {
      document.documentElement.classList.toggle('dark', isDark.value);
    }
  };
  
  return {
    isDark,
    initTheme,
    toggleTheme,
  };
});