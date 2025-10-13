<template>
  <header class="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
    <div class="container">
      <div class="flex h-16 items-center justify-between">
        <!-- Logo -->
        <div class="flex items-center">
          <h1 class="text-2xl font-bold bg-gradient-to-r from-primary to-primary-600 dark:from-primary-300 dark:to-primary-400 bg-clip-text text-transparent">
            AImagine
          </h1>
        </div>

        <!-- Desktop Navigation -->
        <nav class="hidden md:flex">
          <div class="flex space-x-1">
            <Button
              v-for="(item, index) in navItems"
              :key="index"
              :variant="isActive(item.href) ? 'default' : 'ghost'"
              size="sm"
              @click="activeTab = index"
              class="h-9 px-4"
            >
              <a :href="item.href">{{ item.label }}</a>
            </Button>
          </div>
        </nav>

        <!-- Right side -->
        <div class="flex items-center space-x-2">
          <!-- Mobile Menu Button -->
          <Button
            @click="showMobileMenu = !showMobileMenu"
            variant="ghost"
            size="icon"
            class="h-9 w-9 md:hidden"
          >
            <Menu v-if="!showMobileMenu" class="h-4 w-4" />
            <X v-else class="h-4 w-4" />
          </Button>

          <!-- Theme Toggle -->
          <Button
            @click="toggleTheme"
            variant="ghost"
            size="icon"
            class="h-9 w-9 hidden md:flex"
          >
            <Sun v-if="isDark" class="h-4 w-4" />
            <Moon v-else class="h-4 w-4" />
          </Button>

          <!-- User Menu -->
          <DropdownMenu v-if="user && isClient && !authLoading" align="end" class="hidden md:block">
            <template #trigger="{ open }">
              <Button
                variant="outline"
                size="sm"
                class="h-9 px-3"
              >
                {{ user?.username }}
                <ChevronDown class="ml-2 h-4 w-4" />
              </Button>
            </template>

            <DropdownMenuItem @click="window.location.href='/profile'">
              <User class="mr-2 h-4 w-4" />
              个人资料
            </DropdownMenuItem>

            <DropdownMenuItem
              v-if="user?.role === 'admin'"
              @click="window.location.href='/admin'"
            >
              <Settings class="mr-2 h-4 w-4" />
              管理后台
            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem @click="logout" class="text-destructive">
              <LogOut class="mr-2 h-4 w-4" />
              退出登录
            </DropdownMenuItem>
          </DropdownMenu>

          <!-- Auth buttons -->
          <div v-if="(!user || !isClient) && !authLoading" class="hidden md:flex space-x-2">
            <Button @click="navigateToLogin" variant="outline" size="sm" class="h-9 px-4">
              登录
            </Button>
            <Button @click="navigateToRegister" variant="default" size="sm" class="h-9 px-4">
              注册
            </Button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Navigation Menu -->
    <Sheet
      :open="showMobileMenu"
      @update:open="showMobileMenu = $event"
      side="right"
    >
      <SheetHeader class="mb-6">
        <div class="flex items-center justify-between">
          <SheetTitle>菜单</SheetTitle>
          <Button
            @click="showMobileMenu = false"
            variant="ghost"
            size="icon"
            class="h-9 w-9"
          >
            <X class="h-4 w-4" />
          </Button>
        </div>
      </SheetHeader>

      <div class="flex flex-col space-y-4">
        <nav class="flex flex-col space-y-2">
          <Button
            v-for="(item, index) in navItems"
            :key="index"
            :variant="isActive(item.href) ? 'default' : 'ghost'"
            class="w-full justify-start h-9 px-4"
            @click="navigateToMobile(item.href)"
          >
            {{ item.label }}
          </Button>
        </nav>

        <Separator />

        <!-- User section in mobile menu -->
        <div v-if="user && isClient">
          <div class="flex items-center space-x-2 mb-4">
            <User class="h-5 w-5" />
            <span class="font-medium">{{ user?.username }}</span>
          </div>

          <div class="flex flex-col space-y-2">
            <Button
              variant="ghost"
              class="w-full justify-start h-9 px-4"
              @click="navigateToMobile('/profile')"
            >
              <User class="mr-2 h-4 w-4" />
              个人资料
            </Button>

            <Button
              v-if="user?.role === 'admin'"
              variant="ghost"
              class="w-full justify-start h-9 px-4"
              @click="navigateToMobile('/admin')"
            >
              <Settings class="mr-2 h-4 w-4" />
              管理后台
            </Button>

            <Button
              variant="ghost"
              class="w-full justify-start h-9 px-4"
              @click="toggleTheme"
            >
              <Sun v-if="isDark" class="mr-2 h-4 w-4" />
              <Moon v-else class="mr-2 h-4 w-4" />
              {{ isDark ? '浅色模式' : '深色模式' }}
            </Button>

            <Separator />

            <Button
              variant="ghost"
              class="w-full justify-start h-9 px-4 text-destructive"
              @click="logout"
            >
              <LogOut class="mr-2 h-4 w-4" />
              退出登录
            </Button>
          </div>
        </div>

        <!-- Auth buttons in mobile menu -->
        <div v-else>
          <div class="flex flex-col space-y-2">
            <Button
              variant="outline"
              class="w-full justify-start h-9 px-4"
              @click="navigateToMobile('/login')"
            >
              <User class="mr-2 h-4 w-4" />
              登录
            </Button>

            <Button
              variant="default"
              class="w-full justify-start h-9 px-4"
              @click="navigateToMobile('/register')"
            >
              <UserPlus class="mr-2 h-4 w-4" />
              注册
            </Button>

            <Separator />

            <Button
              variant="ghost"
              class="w-full justify-start h-9 px-4"
              @click="toggleTheme"
            >
              <Sun v-if="isDark" class="mr-2 h-4 w-4" />
              <Moon v-else class="mr-2 h-4 w-4" />
              {{ isDark ? '浅色模式' : '深色模式' }}
            </Button>
          </div>
        </div>
      </div>
    </Sheet>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useThemeStore } from '../stores/theme';
import Button from './ui/Button.vue';
import DropdownMenu from './ui/DropdownMenu.vue';
import DropdownMenuItem from './ui/DropdownMenuItem.vue';
import DropdownMenuSeparator from './ui/DropdownMenuSeparator.vue';
import Sheet from './ui/Sheet.vue';
import SheetHeader from './ui/SheetHeader.vue';
import SheetTitle from './ui/SheetTitle.vue';
import Separator from './ui/Separator.vue';
import {
  Menu,
  X,
  Sun,
  Moon,
  User,
  Settings,
  LogOut,
  UserPlus,
  ChevronDown,
} from 'lucide-vue-next';

const authStore = useAuthStore();
const themeStore = useThemeStore();
const user = computed(() => authStore.user);
const isDark = computed(() => themeStore.isDark);
const showUserMenu = ref(false);
const showMobileMenu = ref(false);
const isClient = ref(false);
const authLoading = ref(true);

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
onMounted(async () => {
  isClient.value = true;
  themeStore.initTheme();

  // Set initial active tab based on current path
  const currentPath = window.location.pathname;
  const index = navItems.findIndex(item => item.href === currentPath);
  if (index !== -1) {
    activeTab.value = index;
  }

  // Check authentication state
  if (authStore.token) {
    await authStore.fetchProfile();
  }

  // Short delay to prevent flash
  setTimeout(() => {
    authLoading.value = false;
  }, 50);
});

const toggleTheme = () => {
  themeStore.toggleTheme();
};

const logout = async () => {
  await authStore.logout();
  showUserMenu.value = false;
  window.location.href = '/login';
};

const navigateToMobile = (href: string) => {
  showMobileMenu.value = false;
  window.location.href = href;
};

const navigateToLogin = () => {
  window.location.href = '/login';
};

const navigateToRegister = () => {
  window.location.href = '/register';
};
</script>