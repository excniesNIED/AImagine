<template>
  <div class="min-h-screen">
    <AppHeader />

    <main class="container py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">版本控制</h1>
        <p class="text-gray-600 dark:text-gray-400">查看和管理图片的版本历史记录</p>
      </div>

      <!-- Image Search -->
      <div class="mb-8">
        <div class="flex gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索图片提示词..."
              class="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              @input="debouncedSearch"
            />
          </div>
          <button
            @click="searchImages"
            class="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            搜索
          </button>
        </div>
      </div>

      <!-- Search Results -->
      <div v-if="searchLoading" class="flex justify-center py-12">
        <LoadingAnimation />
      </div>

      <div v-else-if="searchResults.length > 0" class="mb-8">
        <h2 class="text-xl font-semibold mb-4">搜索结果</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div
            v-for="image in searchResults"
            :key="image.id"
            @click="selectImage(image)"
            :class="[
              'group relative aspect-square overflow-hidden rounded-lg cursor-pointer border-2 transition-all duration-200',
              selectedImage?.id === image.id ? 'border-primary-500' : 'border-transparent hover:border-secondary-300'
            ]"
          >
            <img
              :src="image.alist_url"
              :alt="image.prompt"
              class="w-full h-full object-cover"
              loading="lazy"
            />
            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity duration-200">
              <div class="absolute bottom-0 left-0 right-0 p-4 text-white transform translate-y-full group-hover:translate-y-0 transition-transform duration-200">
                <p class="text-sm line-clamp-2">{{ image.prompt }}</p>
                <p class="text-xs mt-1">{{ formatDate(image.created_at) }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Version History -->
      <div v-if="selectedImage && !versionLoading">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold">版本历史</h2>
            <button
              @click="selectedImage = null; versionHistory = []"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              清除选择
            </button>
          </div>

          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <div>
              <h3 class="text-lg font-semibold mb-2">选中图片</h3>
              <div class="aspect-square overflow-hidden rounded-lg">
                <img
                  :src="selectedImage.alist_url"
                  :alt="selectedImage.prompt"
                  class="w-full h-full object-cover"
                />
              </div>
              <div class="mt-4">
                <p class="font-medium">{{ selectedImage.prompt }}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ selectedImage.model.name }} · {{ formatDate(selectedImage.created_at) }}
                </p>
              </div>
            </div>

            <div>
              <h3 class="text-lg font-semibold mb-2">基于此图创作</h3>
              <button
                @click="createNewVersion"
                class="w-full px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors flex items-center justify-center gap-2"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                创建新版本
              </button>
              <div class="mt-4 text-sm text-gray-600 dark:text-gray-400">
                <p>这将打开上传页面，并预填充当前图片的所有元数据，方便您基于此图进行创作。</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Version Tree -->
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h3 class="text-xl font-bold mb-6">版本树</h3>

          <div v-if="versionHistory.length === 0" class="text-center py-8 text-gray-500">
            <p>暂无版本历史</p>
          </div>

          <div v-else class="space-y-6">
            <div
              v-for="version in versionHistory"
              :key="version.id"
              class="flex items-start gap-4 p-4 rounded-lg border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
            >
              <div class="flex-shrink-0">
                <div class="w-16 h-16 overflow-hidden rounded-lg">
                  <img
                    :src="version.alist_url"
                    :alt="version.prompt"
                    class="w-full h-full object-cover"
                  />
                </div>
              </div>

              <div class="flex-1">
                <div class="flex items-center justify-between">
                  <h4 class="font-semibold">版本 {{ getVersionNumber(version) }}</h4>
                  <span class="text-sm text-gray-500">{{ formatDate(version.created_at) }}</span>
                </div>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ version.prompt }}</p>
                <p class="text-xs text-gray-500 mt-2">
                  {{ version.model.name }} · {{ version.category.name }}
                </p>
                <div class="flex items-center gap-2 mt-3">
                  <button
                    @click="openVersionDetail(version)"
                    class="text-primary-500 hover:text-primary-600 text-sm"
                  >
                    查看详情
                  </button>
                  <button
                    @click="createVersionBasedOn(version)"
                    class="text-primary-500 hover:text-primary-600 text-sm"
                  >
                    基于此图创作
                  </button>
                </div>
              </div>

              <div class="flex-shrink-0">
                <div
                  v-if="version.relationship_type === 'parent'"
                  class="w-8 h-8 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center"
                  title="父版本"
                >
                  <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18"></path>
                  </svg>
                </div>
                <div
                  v-else-if="version.relationship_type === 'child'"
                  class="w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center"
                  title="子版本"
                >
                  <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3"></path>
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="versionLoading" class="flex justify-center py-12">
        <LoadingAnimation />
      </div>

      <div v-else-if="!selectedImage" class="text-center py-12">
        <div class="text-gray-400 mb-4">
          <svg class="w-24 h-24 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path>
          </svg>
        </div>
        <p class="text-gray-600 dark:text-gray-400 text-lg">搜索图片以查看其版本历史</p>
        <p class="text-gray-500 dark:text-gray-500 mt-2">输入关键词搜索您想要查看版本历史的图片</p>
      </div>
    </main>

    <!-- Image Detail Modal -->
    <ImageDetailModal
      v-if="selectedVersionDetail"
      :image="selectedVersionDetail"
      @close="selectedVersionDetail = null"
      @update="handleVersionUpdate"
      @delete="handleVersionDelete"
    />

    <!-- Toast Container -->
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from '../utils/axios';
import AppHeader from './AppHeader.vue';
import ImageDetailModal from './ImageDetailModal.vue';
import ToastContainer from './ToastContainer.vue';
import LoadingAnimation from './LoadingAnimation.vue';

interface Image {
  id: number;
  prompt: string;
  negative_prompt: string;
  alist_url: string;
  created_at: string;
  owner_id: number;
  model: { id: number; name: string };
  category: { id: number; name: string };
  tags: { id: number; name: string }[];
  parameters: { key: string; value: string }[];
}

interface VersionHistory extends Image {
  relationship_type: 'parent' | 'child' | 'sibling';
}
const searchQuery = ref('');
const searchResults = ref<Image[]>([]);
const selectedImage = ref<Image | null>(null);
const versionHistory = ref<VersionHistory[]>([]);
const selectedVersionDetail = ref<Image | null>(null);

const searchLoading = ref(false);
const versionLoading = ref(false);

// Debounce search
let searchTimeout: NodeJS.Timeout;
const debouncedSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    if (searchQuery.value.trim()) {
      searchImages();
    }
  }, 500);
};

const searchImages = async () => {
  if (!searchQuery.value.trim()) return;

  try {
    searchLoading.value = true;
    const response = await axios.get('/api/v1/images', {
      params: {
        search: searchQuery.value,
        limit: 20
      }
    });
    searchResults.value = response.data.items;
  } catch (error) {
    console.error('Failed to search images:', error);
  } finally {
    searchLoading.value = false;
  }
};

const selectImage = async (image: Image) => {
  selectedImage.value = image;
  await fetchVersionHistory(image.id);
};

const fetchVersionHistory = async (imageId: number) => {
  try {
    versionLoading.value = true;
    const response = await axios.get(`/api/v1/images/${imageId}/versions`);

    // Add relationship type to each version
    versionHistory.value = response.data.map((version: any) => {
      let relationshipType: 'parent' | 'child' | 'sibling' = 'sibling';

      if (version.id === imageId) {
        relationshipType = 'parent'; // This is the root/selected image
      } else if (version.parent_image_id === imageId) {
        relationshipType = 'child';
      } else if (version.parent_image_id) {
        relationshipType = 'child';
      }

      return {
        ...version,
        relationship_type: relationshipType
      };
    });
  } catch (error) {
    console.error('Failed to fetch version history:', error);
    versionHistory.value = [];
  } finally {
    versionLoading.value = false;
  }
};

const getVersionNumber = (version: VersionHistory): string => {
  // This would be implemented based on your version numbering logic
  const index = versionHistory.value.findIndex(v => v.id === version.id);
  return `v${index + 1}`;
};

const createNewVersion = () => {
  if (!selectedImage.value) return;
  createVersionBasedOn(selectedImage.value);
};

const createVersionBasedOn = (image: Image) => {
  // Navigate to upload page with query parameters
  const params = new URLSearchParams({
    parent_image_id: image.id.toString(),
    prompt: image.prompt,
    model_id: image.model.id.toString(),
    category_id: image.category.id.toString(),
    tags: image.tags.map(tag => tag.id).join(',')
  });

  if (image.negative_prompt) {
    params.append('negative_prompt', image.negative_prompt);
  }

  window.location.href = `/upload?${params.toString()}`;
};

const openVersionDetail = (version: Image) => {
  selectedVersionDetail.value = version;
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const handleVersionUpdate = (updatedImage: Image) => {
  const index = versionHistory.value.findIndex(v => v.id === updatedImage.id);
  if (index > -1) {
    versionHistory.value[index] = updatedImage;
  }
  selectedVersionDetail.value = updatedImage;
};

const handleVersionDelete = (imageId: number) => {
  versionHistory.value = versionHistory.value.filter(v => v.id !== imageId);
  selectedVersionDetail.value = null;
};

onMounted(() => {
  // Initialize with empty state
});
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>