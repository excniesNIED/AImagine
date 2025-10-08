<template>
  <div class="min-h-screen">
    <AppHeader />

    <main class="container py-8">
      <h1 class="text-3xl font-bold mb-8">管理后台</h1>

      <!-- Dashboard Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">用户总数</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.users }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">图片总数</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.images }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">分类数量</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.categories }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">标签数量</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.tags }}</p>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
          <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">模型数量</h3>
          <p class="text-2xl font-bold mt-2">{{ stats.models }}</p>
        </div>
      </div>

      <!-- Admin Navigation Tabs -->
      <div class="border-b border-gray-200 dark:border-gray-700 mb-8">
        <nav class="-mb-px flex space-x-8">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              'py-2 px-1 border-b-2 font-medium text-sm transition-colors',
              activeTab === tab.key
                ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
            ]"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>

      <!-- Tab Content -->
      <div>
        <!-- Dashboard -->
        <div v-if="activeTab === 'dashboard'" class="space-y-6">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
            <h2 class="text-xl font-semibold mb-4">最近上传的图片</h2>
            <div class="space-y-4">
              <div v-for="image in recentImages" :key="image.id" class="flex items-center space-x-4">
                <img :src="image.alist_url" :alt="image.prompt" class="w-16 h-16 object-cover rounded" />
                <div class="flex-1">
                  <p class="font-medium">{{ image.prompt.substring(0, 100) }}...</p>
                  <p class="text-sm text-gray-500">用户ID: {{ image.owner_id }} | {{ formatDate(image.created_at) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Images Management -->
        <ImagesManager v-if="activeTab === 'images'" />

        <!-- Categories Management -->
        <CategoriesManager v-if="activeTab === 'categories'" />

        <!-- Tags Management -->
        <TagsManager v-if="activeTab === 'tags'" />

        <!-- Models Management -->
        <ModelsManager v-if="activeTab === 'models'" />

        <!-- Users Management -->
        <UsersManager v-if="activeTab === 'users'" />

        <!-- Settings -->
        <SettingsManager v-if="activeTab === 'settings'" />
      </div>
    </main>

    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from '../utils/axios';
import AppHeader from './AppHeader.vue';
import ToastContainer from './ToastContainer.vue';
import ImagesManager from './admin/ImagesManager.vue';
import CategoriesManager from './admin/CategoriesManager.vue';
import TagsManager from './admin/TagsManager.vue';
import ModelsManager from './admin/ModelsManager.vue';
import UsersManager from './admin/UsersManager.vue';
import SettingsManager from './admin/SettingsManager.vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

interface Stats {
  users: number;
  images: number;
  categories: number;
  tags: number;
  models: number;
}

interface Image {
  id: number;
  prompt: string;
  alist_url: string;
  owner_id: number;
  created_at: string;
}

const tabs = [
  { key: 'dashboard', label: '仪表盘' },
  { key: 'images', label: '作品管理' },
  { key: 'categories', label: '分类管理' },
  { key: 'tags', label: '标签管理' },
  { key: 'models', label: '模型管理' },
  { key: 'users', label: '用户管理' },
  { key: 'settings', label: '系统设置' }
];

const activeTab = ref('dashboard');
const stats = ref<Stats>({
  users: 0,
  images: 0,
  categories: 0,
  tags: 0,
  models: 0
});
const recentImages = ref<Image[]>([]);

const fetchDashboardData = async () => {
  try {
    const response = await axios.get('/api/v1/admin/dashboard');
    stats.value = response.data.stats;
    recentImages.value = response.data.recent_images;
  } catch (error) {
    console.error('Failed to fetch dashboard data:', error);
  }
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN');
};

onMounted(() => {
  fetchDashboardData();
});
</script>