<template>
  <div class="min-h-screen">
    <AppHeader />
    
    <main class="container py-8">
      <!-- Search and Filter Bar -->
      <div class="mb-8 space-y-4">
        <div class="flex flex-col md:flex-row gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索提示词、模型或标签..."
              class="w-full px-4 py-2 border border-border-light dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              @input="debouncedSearch"
            />
          </div>
          
          <select
            v-model="selectedCategory"
            class="px-4 py-2 border border-border-light dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500"
            @change="filterImages"
          >
            <option value="">所有分类</option>
            <option v-for="category in categories" :key="category.id" :value="category.id">
              {{ category.name }}
            </option>
          </select>

          <select
            v-model="selectedModel"
            class="px-4 py-2 border border-border-light dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500"
            @change="filterImages"
          >
            <option value="">所有模型</option>
            <option v-for="model in models" :key="model.id" :value="model.id">
              {{ model.name }}
            </option>
          </select>
        </div>
        
        <!-- Tags Filter -->
        <div class="flex flex-wrap gap-2" v-if="tags.length">
          <button
            v-for="tag in tags"
            :key="tag.id"
            @click="toggleTag(tag.id)"
            :class="[
              'px-3 py-1 rounded-full text-sm transition-colors',
              selectedTags.includes(tag.id)
                ? 'bg-primary-500 text-white'
                : 'bg-background-accent dark:bg-gray-700 text-text-primary dark:text-gray-300 hover:bg-secondary-100 dark:hover:bg-gray-600'
            ]"
          >
            {{ tag.name }}
          </button>
        </div>
      </div>
      
      <!-- Gallery Grid -->
      <div v-if="loading" class="flex justify-center py-12">
        <LoadingAnimation />
      </div>
      
      <div v-else-if="images.length === 0" class="text-center py-12">
        <p class="text-text-secondary dark:text-gray-400">暂无图片</p>
      </div>
      
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <div
          v-for="image in images"
          :key="image.id"
          @click="openImage(image)"
          class="group relative aspect-square overflow-hidden rounded-lg cursor-pointer transform transition-all duration-200 hover:scale-105"
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
              <div class="flex items-center justify-between mt-2 text-xs">
                <span>{{ image.model.name }}</span>
                <span>{{ formatDate(image.created_at) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Load More -->
      <div v-if="hasMore && !loading" class="text-center mt-8">
        <button
          @click="loadMore"
          class="btn-primary"
        >
          加载更多
        </button>
      </div>
    </main>
    
    <!-- Image Detail Modal -->
    <ImageDetailModal
      v-if="selectedImage"
      :image="selectedImage"
      @close="selectedImage = null"
      @update="handleImageUpdate"
      @delete="handleImageDelete"
    />
    
    <!-- Toast Container -->
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from '../utils/axios';
import AppHeader from './AppHeader.vue';
import ImageDetailModal from './ImageDetailModal.vue';
import ToastContainer from './ToastContainer.vue';
import LoadingAnimation from './LoadingAnimation.vue';
import { useAuthStore } from '../stores/auth';

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

interface Category {
  id: number;
  name: string;
}

interface Model {
  id: number;
  name: string;
}

interface Tag {
  id: number;
  name: string;
}

const images = ref<Image[]>([]);
const authStore = useAuthStore();
const categories = ref<Category[]>([]);
const models = ref<Model[]>([]);
const tags = ref<Tag[]>([]);
const loading = ref(true);
const hasMore = ref(true);
const page = ref(1);
const pageSize = 20;

// Filters
const searchQuery = ref('');
const selectedCategory = ref('');
const selectedModel = ref('');
const selectedTags = ref<number[]>([]);

const selectedImage = ref<Image | null>(null);

// Debounce search
let searchTimeout: NodeJS.Timeout;
const debouncedSearch = () => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    page.value = 1;
    images.value = [];
    fetchImages();
  }, 500);
};

const fetchImages = async () => {
  try {
    loading.value = true;
    // If not authenticated, do not call protected endpoint; just show empty state
    if (!authStore.isAuthenticated) {
      images.value = [];
      hasMore.value = false;
      loading.value = false;
      return;
    }
    const params: any = {
      skip: (page.value - 1) * pageSize,
      limit: pageSize,
    };
    
    if (searchQuery.value) params.search = searchQuery.value;
    if (selectedCategory.value) params.category_id = selectedCategory.value;
    if (selectedModel.value) params.model_id = selectedModel.value;
    if (selectedTags.value.length) params.tag_ids = selectedTags.value.join(',');
    
    const response = await axios.get('/api/v1/images/', { params });
    
    if (page.value === 1) {
      images.value = response.data.items;
    } else {
      images.value.push(...response.data.items);
    }
    
    hasMore.value = response.data.items.length === pageSize;
  } catch (error) {
    // Avoid noisy logs on 401; other errors can still surface in toast if needed
    if ((error as any)?.response?.status !== 401) {
      console.error('Failed to fetch images:', error);
    }
    images.value = [];
    hasMore.value = false;
  } finally {
    loading.value = false;
  }
};

const fetchCategories = async () => {
  try {
    const response = await axios.get('/api/v1/categories');
    categories.value = response.data;
  } catch (error) {
    console.error('Failed to fetch categories:', error);
  }
};

const fetchModels = async () => {
  try {
    const response = await axios.get('/api/v1/models');
    models.value = response.data;
  } catch (error) {
    console.error('Failed to fetch models:', error);
  }
};

const fetchTags = async () => {
  try {
    const response = await axios.get('/api/v1/tags');
    tags.value = response.data;
  } catch (error) {
    console.error('Failed to fetch tags:', error);
  }
};

const filterImages = () => {
  page.value = 1;
  images.value = [];
  fetchImages();
};

const toggleTag = (tagId: number) => {
  const index = selectedTags.value.indexOf(tagId);
  if (index > -1) {
    selectedTags.value.splice(index, 1);
  } else {
    selectedTags.value.push(tagId);
  }
  filterImages();
};

const loadMore = () => {
  page.value++;
  fetchImages();
};

const openImage = (image: Image) => {
  selectedImage.value = image;
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN');
};

const handleImageUpdate = (updatedImage: Image) => {
  const index = images.value.findIndex(img => img.id === updatedImage.id);
  if (index > -1) {
    images.value[index] = updatedImage;
  }
  selectedImage.value = updatedImage;
};

const handleImageDelete = (imageId: number) => {
  images.value = images.value.filter(img => img.id !== imageId);
  selectedImage.value = null;
};

onMounted(() => {
  Promise.all([
    fetchImages(),
    fetchCategories(),
    fetchModels(),
    fetchTags(),
  ]);
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