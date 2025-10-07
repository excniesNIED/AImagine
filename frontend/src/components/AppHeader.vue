<template>
  <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-border-light dark:border-gray-700">
    <div class="container">
      <div class="flex justify-between items-center h-16">
        <!-- Logo -->
        <div class="flex items-center">
          <h1 class="text-xl font-bold text-primary-500 dark:text-primary-300">
            AImagine
          </h1>
        </div>

        <!-- Navigation -->
        <nav class="hidden md:flex space-x-8">
          <a href="/" class="text-text-primary dark:text-gray-200 hover:text-primary-500 dark:hover:text-primary-300 transition-colors">
            我的画廊
          </a>
          <a href="/square" class="text-text-primary dark:text-gray-200 hover:text-primary-500 dark:hover:text-primary-300 transition-colors">
            作品广场
          </a>
          <a href="/upload" class="text-text-primary dark:text-gray-200 hover:text-primary-500 dark:hover:text-primary-300 transition-colors">
            上传
          </a>
          <a href="/search" class="text-text-primary dark:text-gray-200 hover:text-primary-500 dark:hover:text-primary-300 transition-colors">
            版本控制
          </a>
        </nav>
        
        <!-- Right side -->
        <div class="flex items-center space-x-4">
          <!-- Theme Toggle -->
          <button
            @click="toggleTheme"
            class="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
          >
            <svg v-if="isDark" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
            </svg>
          </button>
          
          <!-- User Menu -->
          <div class="relative" v-if="user">
            <button
              @click="showUserMenu = !showUserMenu"
              class="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            >
              <span class="text-sm font-medium">{{ user.username }}</span>
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>
            
            <div v-if="showUserMenu" class="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-border-light dark:border-gray-700">
              <a href="/profile" class="block px-4 py-2 text-sm text-text-primary dark:text-gray-200 hover:bg-background-light dark:hover:bg-gray-700">
                个人资料
              </a>
              <a v-if="user.role === 'admin'" href="/admin" class="block px-4 py-2 text-sm text-text-primary dark:text-gray-200 hover:bg-background-light dark:hover:bg-gray-700">
                管理后台
              </a>
              <button
                @click="logout"
                class="w-full text-left px-4 py-2 text-sm text-text-primary dark:text-gray-200 hover:bg-background-light dark:hover:bg-gray-700"
              >
                退出登录
              </button>
            </div>
          </div>
          
          <div v-else class="flex space-x-2">
            <a href="/login" class="btn-primary">登录</a>
            <a href="/register" class="btn-secondary">注册</a>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useThemeStore } from '../stores/theme';

const authStore = useAuthStore();
const themeStore = useThemeStore();
const user = computed(() => authStore.user);
const isDark = computed(() => themeStore.isDark);
const showUserMenu = ref(false);

const toggleTheme = () => {
  themeStore.toggleTheme();
};

const logout = async () => {
  await authStore.logout();
  // Soft redirect to login to ensure clean state
  window.location.href = '/login';
};

onMounted(() => {
  themeStore.initTheme();
});
</script>