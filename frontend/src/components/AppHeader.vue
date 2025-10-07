<template>
  <header class="app-header bg-white dark:bg-gray-800 shadow-sm border-b border-border-light dark:border-gray-700">
    <div class="container">
      <div class="flex justify-between items-center h-20">
        <!-- Logo -->
        <div class="flex items-center">
          <h1 class="text-2xl font-bold bg-gradient-to-r from-primary-500 to-primary-600 dark:from-primary-300 dark:to-primary-400 bg-clip-text text-transparent">
            AImagine
          </h1>
        </div>

        <!-- Desktop Navigation with Glider -->
        <nav class="hidden md:block">
          <div class="nav-tabs bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200">
            <a 
              v-for="(item, index) in navItems" 
              :key="index"
              :href="item.href" 
              :class="['nav-tab', { 'active': isActive(item.href) }, item.href === '/square' ? 'font-bold' : '']"
              @click="activeTab = index"
            >
              {{ item.label }}
            </a>
            <span class="nav-glider dark:bg-gray-700" :style="{ transform: `translateX(${activeTab * 100}%)` }"></span>
          </div>
        </nav>
        
        <!-- Right side -->
        <div class="flex items-center space-x-4">
          <!-- Mobile Menu Button (only on mobile) -->
          <button
            @click="showMobileMenu = !showMobileMenu"
            class="mobile-menu-btn inline-flex items-center justify-center md:hidden"
          >
            <svg v-if="!showMobileMenu" class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
            <svg v-else class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>

          <!-- Theme Toggle (hidden on mobile) -->
          <button
            @click="toggleTheme"
            class="theme-toggle hidden md:flex"
          >
            <svg v-if="isDark" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>
            </svg>
            <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
            </svg>
          </button>
          
          <!-- User Menu (hidden on mobile) -->
          <div class="relative user-menu-container z-50 hidden md:block" v-if="user">
            <button
              @click="showUserMenu = !showUserMenu"
              class="user-menu-button"
            >
              <span class="text-sm font-medium">{{ user.username }}</span>
              <svg 
                class="w-4 h-4 transition-transform duration-200" 
                :class="{ 'rotate-180': showUserMenu }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
              </svg>
            </button>
            
            <transition name="dropdown">
              <div v-if="showUserMenu" class="user-dropdown z-50 bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-200 dark:border-gray-700">
                <a href="/profile" class="dropdown-item">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                  </svg>
                  个人资料
                </a>
                <a v-if="user.role === 'admin'" href="/admin" class="dropdown-item">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                  </svg>
                  管理后台
                </a>
                <div class="dropdown-divider"></div>
                <button
                  @click="logout"
                  class="dropdown-item logout-item"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
                  </svg>
                  退出登录
                </button>
              </div>
            </transition>
          </div>
          
          <!-- Auth buttons (hidden on mobile) -->
          <div v-else class="hidden md:flex space-x-2">
            <a href="/login" class="auth-btn auth-btn-login">登录</a>
            <a href="/register" class="auth-btn auth-btn-register">注册</a>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation Menu -->
    <transition name="mobile-menu">
      <div v-if="showMobileMenu" class="mobile-menu md:hidden bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-200 z-50">
        <div class="mobile-nav-container">
          <a 
            v-for="(item, index) in navItems" 
            :key="index"
            :href="item.href" 
            :class="['mobile-nav-item', { 'active': isActive(item.href) }]"
            @click="showMobileMenu = false"
          >
            {{ item.label }}
          </a>

          <!-- User section in mobile menu -->
          <div v-if="user" class="mobile-user-section">
            <div class="mobile-divider"></div>
            <div class="mobile-user-info">
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
              <span>{{ user.username }}</span>
            </div>
            <a href="/profile" class="mobile-nav-item" @click="showMobileMenu = false">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
              个人资料
            </a>
            <a v-if="user.role === 'admin'" href="/admin" class="mobile-nav-item" @click="showMobileMenu = false">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              </svg>
              管理后台
            </a>
            <button @click="logout" class="mobile-nav-item logout-mobile">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
              退出登录
            </button>
            <div class="mobile-divider"></div>
            <button @click="toggleTheme" class="mobile-nav-item">
              <svg v-if="isDark" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>
              </svg>
              <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
              </svg>
              {{ isDark ? '浅色模式' : '深色模式' }}
            </button>
          </div>

          <!-- Auth buttons in mobile menu -->
          <div v-else class="mobile-auth-section">
            <div class="mobile-divider"></div>
            <a href="/login" class="mobile-nav-item">登录</a>
            <a href="/register" class="mobile-nav-item active">注册</a>
            <div class="mobile-divider"></div>
            <button @click="toggleTheme" class="mobile-nav-item">
              <svg v-if="isDark" class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clip-rule="evenodd"></path>
              </svg>
              <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"></path>
              </svg>
              {{ isDark ? '浅色模式' : '深色模式' }}
            </button>
          </div>
        </div>
      </div>
    </transition>
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
const showMobileMenu = ref(false);
const isClient = ref(false);

// Navigation items
const navItems = [
  { label: '我的画廊', href: '/' },
  { label: '作品广场', href: '/square' },
  { label: '上传', href: '/upload' },
  { label: '版本控制', href: '/search' }
];

// Active tab tracking
const activeTab = ref(0);

// Check if current path matches the nav item
const isActive = (href: string) => {
  if (!isClient.value) return false;
  const currentPath = window.location.pathname;
  return currentPath === href || (href === '/' && currentPath === '/');
};

// Initialize active tab on mount
onMounted(() => {
  isClient.value = true;
  themeStore.initTheme();
  
  // Set initial active tab based on current path
  const currentPath = window.location.pathname;
  const index = navItems.findIndex(item => item.href === currentPath);
  if (index !== -1) {
    activeTab.value = index;
  }
});

const toggleTheme = () => {
  themeStore.toggleTheme();
};

const logout = async () => {
  await authStore.logout();
  showUserMenu.value = false;
  // Soft redirect to login to ensure clean state
  window.location.href = '/login';
};
</script>

<style scoped>
/* Header positioning for mobile menu */
.app-header {
  position: relative;
}

/* Navigation Tabs with Glider Effect */
.nav-tabs {
  display: flex;
  position: relative;
  background-color: transparent;
  box-shadow: 0 0 1px 0 rgba(24, 94, 224, 0.15), 0 6px 12px 0 rgba(24, 94, 224, 0.15);
  padding: 0.5rem;
  border-radius: 99px;
  gap: 0.25rem;
}

:global(.dark) .nav-tabs {
  background-color: transparent;
  box-shadow: 0 0 1px 0 rgba(99, 102, 241, 0.2), 0 6px 12px 0 rgba(99, 102, 241, 0.15);
}

.nav-tabs * {
  z-index: 2;
}

.nav-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 38px;
  min-width: 90px;
  padding: 0 1.25rem;
  font-size: 0.875rem;
  color: #374151;
  font-weight: 500;
  border-radius: 99px;
  cursor: pointer;
  transition: color 0.25s ease-in-out;
  text-decoration: none;
  position: relative;
}

:global(.dark) .nav-tab {
  color: #9ca3af;
}

.nav-tab:hover {
  color: #185ee0;
}

:global(.dark) .nav-tab:hover {
  color: #818cf8;
}

.nav-tab.active {
  color: #185ee0;
  font-weight: 600;
}

:global(.dark) .nav-tab.active {
  color: #818cf8;
}

.nav-glider {
  position: absolute;
  display: flex;
  height: 38px;
  width: calc((100% - 1rem) / 4);
  background: linear-gradient(135deg, #e6eef9 0%, #dae5f7 100%);
  z-index: 1;
  border-radius: 99px;
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  left: 0.5rem;
}

:global(.dark) .nav-glider {
  background: linear-gradient(135deg, #312e81 0%, #3730a3 100%);
}

/* Theme Toggle Button */
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0.5rem;
  color: #6b7280;
  background-color: #f9fafb;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

:global(.dark) .theme-toggle {
  color: #9ca3af;
  background-color: #374151;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
}

.theme-toggle:hover {
  color: #185ee0;
  background-color: #e6eef9;
  transform: scale(1.05);
}

:global(.dark) .theme-toggle:hover {
  color: #818cf8;
  background-color: #4b5563;
  transform: scale(1.05);
}

.theme-toggle:active {
  transform: scale(0.95);
}

/* User Menu Container */
.user-menu-container {
  position: relative;
}

.user-menu-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #fff 0%, #f9fafb 100%);
  border: 1px solid #e5e7eb;
  border-radius: 99px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  color: #374151;
  font-weight: 500;
}

:global(.dark) .user-menu-button {
  background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
  border-color: #4b5563;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
  color: #e5e7eb;
}

.user-menu-button:hover {
  background: linear-gradient(135deg, #e6eef9 0%, #dae5f7 100%);
  border-color: #185ee0;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px -1px rgba(24, 94, 224, 0.1);
}

:global(.dark) .user-menu-button:hover {
  background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
  border-color: #818cf8;
  box-shadow: 0 4px 6px -1px rgba(129, 140, 248, 0.2);
}

.user-menu-button:active {
  transform: translateY(0);
}

/* User Dropdown */
.user-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 0.5rem);
  min-width: 200px;
  background: transparent;
  border-radius: 16px;
  box-shadow: 0 0 1px 0 rgba(24, 94, 224, 0.15), 
              0 10px 25px -5px rgba(24, 94, 224, 0.2),
              0 20px 25px -5px rgba(24, 94, 224, 0.1);
  border: none;
  overflow: hidden;
  padding: 0.5rem;
}

:global(.dark) .user-dropdown {
  background: transparent;
  border-color: transparent;
  box-shadow: 0 0 1px 0 rgba(99, 102, 241, 0.2), 
              0 10px 25px -5px rgba(99, 102, 241, 0.3),
              0 20px 25px -5px rgba(0, 0, 0, 0.5);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #374151;
  text-align: left;
  text-decoration: none;
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.15s ease-in-out;
  font-weight: 500;
}

:global(.dark) .dropdown-item {
  color: #e5e7eb;
}

.dropdown-item:hover {
  background: linear-gradient(135deg, #e6eef9 0%, #dae5f7 100%);
  color: #185ee0;
  transform: translateX(2px);
}

:global(.dark) .dropdown-item:hover {
  background: linear-gradient(135deg, #312e81 0%, #3730a3 100%);
  color: #818cf8;
}

.dropdown-item svg {
  flex-shrink: 0;
  transition: transform 0.15s ease-in-out;
}

.dropdown-item:hover svg {
  transform: scale(1.1);
}

.logout-item {
  color: #dc2626;
}

:global(.dark) .logout-item {
  color: #f87171;
}

.logout-item:hover {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
}

:global(.dark) .logout-item:hover {
  background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
  color: #fca5a5;
}

.dropdown-divider {
  height: 1px;
  margin: 0.5rem 0;
  background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
}

:global(.dark) .dropdown-divider {
  background: linear-gradient(90deg, transparent, #4b5563, transparent);
}

/* Dropdown Animation */
.dropdown-enter-active {
  animation: dropdown-in 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.dropdown-leave-active {
  animation: dropdown-out 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes dropdown-in {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes dropdown-out {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
}

/* Auth Buttons */
.auth-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  border-radius: 99px;
  text-decoration: none;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  border: 1px solid transparent;
}

.auth-btn-login {
  background: linear-gradient(135deg, #fff 0%, #f9fafb 100%);
  color: #185ee0;
  border-color: #185ee0;
}

:global(.dark) .auth-btn-login {
  background: linear-gradient(135deg, #374151 0%, #1f2937 100%);
  color: #818cf8;
  border-color: #818cf8;
}

.auth-btn-login:hover {
  background: linear-gradient(135deg, #e6eef9 0%, #dae5f7 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(24, 94, 224, 0.2);
}

:global(.dark) .auth-btn-login:hover {
  background: linear-gradient(135deg, #4b5563 0%, #374151 100%);
  box-shadow: 0 4px 6px -1px rgba(129, 140, 248, 0.3);
}

.auth-btn-register {
  background: linear-gradient(135deg, #185ee0 0%, #1d4ed8 100%);
  color: #fff;
}

:global(.dark) .auth-btn-register {
  background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%);
  color: #1f2937;
}

.auth-btn-register:hover {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(24, 94, 224, 0.4);
}

:global(.dark) .auth-btn-register:hover {
  background: linear-gradient(135deg, #818cf8 0%, #a5b4fc 100%);
  box-shadow: 0 4px 6px -1px rgba(129, 140, 248, 0.5);
}

.auth-btn:active {
  transform: translateY(0);
}

/* Mobile Menu Button */
.mobile-menu-btn {
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0.5rem;
  color: #374151;
  background-color: #f9fafb;
  border-radius: 10px;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

:global(.dark) .mobile-menu-btn {
  color: #e5e7eb;
  background-color: #374151;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.3);
}

.mobile-menu-btn:hover {
  background-color: #e6eef9;
  color: #185ee0;
  transform: scale(1.05);
}

:global(.dark) .mobile-menu-btn:hover {
  background-color: #4b5563;
  color: #818cf8;
}

.mobile-menu-btn:active {
  transform: scale(0.95);
}

/* Mobile Menu */
.mobile-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #fff;
  border-top: 1px solid #e5e7eb;
  box-shadow: 0 10px 25px -5px rgba(24, 94, 224, 0.1);
  z-index: 50;
}

:global(.dark) .mobile-menu {
  background: #1f2937;
  border-top-color: #374151;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
}

.mobile-nav-container {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.mobile-nav-item {
  display: flex;
  align-items: center;
  padding: 0.875rem 1.25rem;
  color: #374151;
  font-weight: 500;
  text-decoration: none;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.2s ease-in-out;
  position: relative;
  overflow: hidden;
}

:global(.dark) .mobile-nav-item {
  color: #e5e7eb;
  background: #374151;
}

.mobile-nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #185ee0 0%, #1d4ed8 100%);
  transform: scaleY(0);
  transition: transform 0.2s ease-in-out;
}

:global(.dark) .mobile-nav-item::before {
  background: linear-gradient(180deg, #6366f1 0%, #818cf8 100%);
}

.mobile-nav-item.active::before {
  transform: scaleY(1);
}

.mobile-nav-item.active {
  background: linear-gradient(135deg, #e6eef9 0%, #dae5f7 100%);
  color: #185ee0;
  font-weight: 600;
}

:global(.dark) .mobile-nav-item.active {
  background: linear-gradient(135deg, #312e81 0%, #3730a3 100%);
  color: #818cf8;
}

.mobile-nav-item:hover {
  background: linear-gradient(135deg, #e6eef9 0%, #dae5f7 100%);
  color: #185ee0;
  transform: translateX(4px);
}

:global(.dark) .mobile-nav-item:hover {
  background: linear-gradient(135deg, #312e81 0%, #3730a3 100%);
  color: #818cf8;
}

/* Mobile User Section */
.mobile-user-section,
.mobile-auth-section {
  margin-top: 0.5rem;
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  color: #185ee0;
  font-weight: 600;
  background: linear-gradient(135deg, #e6eef9 0%, #dae5f7 100%);
  border-radius: 12px;
  margin-bottom: 0.5rem;
}

:global(.dark) .mobile-user-info {
  color: #818cf8;
  background: linear-gradient(135deg, #312e81 0%, #3730a3 100%);
}

.mobile-divider {
  height: 1px;
  margin: 0.75rem 0;
  background: linear-gradient(90deg, transparent, #e5e7eb, transparent);
}

:global(.dark) .mobile-divider {
  background: linear-gradient(90deg, transparent, #4b5563, transparent);
}

.logout-mobile {
  color: #dc2626;
  width: 100%;
  text-align: left;
  border: none;
  cursor: pointer;
}

:global(.dark) .logout-mobile {
  color: #f87171;
}

.logout-mobile:hover {
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
  color: #991b1b;
}

:global(.dark) .logout-mobile:hover {
  background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
  color: #fca5a5;
}

/* Mobile Menu Animation */
.mobile-menu-enter-active {
  animation: mobile-slide-in 0.3s ease-out;
}

.mobile-menu-leave-active {
  animation: mobile-slide-out 0.2s ease-in;
}

@keyframes mobile-slide-in {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes mobile-slide-out {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-20px);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .nav-tabs {
    transform: scale(0.85);
  }
}

/* Hide mobile menu button in landscape orientation on small screens */
@media (orientation: landscape) and (max-width: 768px) {
  .mobile-menu-btn {
    display: none;
  }
}
</style>