<template>
  <div class="min-h-screen">
    <AppHeader />
    
    <main class="container py-8">
      <div class="mb-8">
        <h1 class="text-3xl font-bold mb-2">作品广场</h1>
        <p class="text-gray-600 dark:text-gray-400">发现和探索其他用户公开分享的精彩作品</p>
      </div>

      <!-- Search and Filter Bar -->
      <div class="mb-8 space-y-4">
        <div class="flex flex-col md:flex-row md:items-center gap-4">
          <div class="flex-1">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索提示词、模型或标签..."
              class="w-full px-4 py-2 border border-border-light dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all hover:border-primary-300 dark:hover:border-primary-700"
              @input="debouncedSearch"
            />
          </div>
          
          <div class="flex flex-col sm:flex-row gap-4 md:flex-none md:w-auto">
            <DropdownSelect
              v-model="selectedCategory"
              :options="categoryOptions"
              placeholder="所有分类"
              @change="filterImages"
              class="w-full sm:w-48"
            />

            <DropdownSelect
              v-model="selectedModel"
              :options="modelOptions"
              placeholder="所有模型"
              @change="filterImages"
              class="w-full sm:w-48"
            />
          </div>
        </div>
        
        <!-- Tags Filter -->
        <div class="flex flex-wrap gap-2" v-if="tags.length">
          <button
            v-for="tag in tags"
            :key="tag.id"
            @click="toggleTag(tag.id)"
            :class="[
              'px-3 py-1 rounded-full text-sm transition-all font-medium',
              selectedTags.includes(tag.id)
                ? 'bg-primary-500 text-white shadow-md'
                : 'bg-background-accent dark:bg-gray-700 text-text-primary dark:text-gray-300 hover:bg-secondary-100 dark:hover:bg-gray-600 hover:shadow-sm'
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
        <svg class="w-24 h-24 mx-auto text-gray-300 dark:text-gray-700 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
        </svg>
        <p class="text-text-secondary dark:text-gray-400 text-lg">暂无公开作品</p>
        <p class="text-gray-500 dark:text-gray-500 text-sm mt-2">用户可以在上传作品时选择公开分享</p>
      </div>
      
      <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
        <div
          v-for="image in images"
          :key="image.id"
          @click="selectedImage = image"
          class="card overflow-hidden cursor-pointer hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 group"
        >
          <div class="aspect-square overflow-hidden bg-gray-100 dark:bg-gray-800">
            <img
              :src="image.alist_url"
              :alt="image.prompt"
              class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
              loading="lazy"
            />
          </div>
          <div class="p-3">
            <p class="text-sm text-text-primary dark:text-gray-300 line-clamp-2 mb-2 font-medium">
              {{ image.prompt }}
            </p>
            <div class="flex items-center justify-between text-xs text-text-secondary dark:text-gray-500">
              <span v-if="image.model">{{ image.model.name }}</span>
              <span v-else-if="image.custom_model">{{ image.custom_model }}</span>
              <span>{{ formatDate(image.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore && !loading" class="mt-8 text-center">
        <button
          @click="loadMore"
          class="btn-primary px-8 py-3"
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
      @refresh="fetchImages"
    />
    
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
import DropdownSelect from './DropdownSelect.vue';

interface Image {
  id: number;
  prompt: string;
  negative_prompt: string;
  alist_url: string;
  created_at: string;
  owner_id: number;
  custom_model?: string;
  custom_category?: string;
  model: { id: number; name: string } | null;
  category: { id: number; name: string } | null;
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

const categoryOptions = computed(() => {
  const opts = categories.value.map(c => ({ value: c.id, label: c.name }));
  return [{ value: '', label: '所有分类' }, ...opts];
});

const modelOptions = computed(() => {
  const opts = models.value.map(m => ({ value: m.id, label: m.name }));
  return [{ value: '', label: '所有模型' }, ...opts];
});

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
    
    const params: any = {
      skip: (page.value - 1) * pageSize,
      limit: pageSize
    };
    
    if (searchQuery.value) params.search = searchQuery.value;
    if (selectedCategory.value) params.category_id = selectedCategory.value;
    if (selectedModel.value) params.model_id = selectedModel.value;
    if (selectedTags.value.length) params.tag_ids = selectedTags.value.join(',');
    
    const response = await axios.get('/api/v1/images/public', { params });
    
    if (page.value === 1) {
      images.value = response.data.items;
    } else {
      images.value.push(...response.data.items);
    }
    
    hasMore.value = images.value.length < response.data.total;
  } catch (error) {
    console.error('Failed to fetch images:', error);
  } finally {
    loading.value = false;
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

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  
  if (days === 0) return '今天';
  if (days === 1) return '昨天';
  if (days < 7) return `${days}天前`;
  if (days < 30) return `${Math.floor(days / 7)}周前`;
  if (days < 365) return `${Math.floor(days / 30)}个月前`;
  return `${Math.floor(days / 365)}年前`;
};

onMounted(async () => {
  try {
    const [categoriesRes, modelsRes, tagsRes] = await Promise.all([
      axios.get('/api/v1/categories/'),
      axios.get('/api/v1/models/'),
      axios.get('/api/v1/tags/')
    ]);

    categories.value = categoriesRes.data;
    models.value = modelsRes.data;
    tags.value = tagsRes.data;
    
    await fetchImages();
  } catch (error) {
    console.error('Failed to load initial data:', error);
  }
});
</script>

