<template>
  <div class="min-h-screen">
    <AppHeader />
    
    <main class="container py-8 max-w-4xl mx-auto">
      <h1 class="text-3xl font-bold mb-8">
        {{ isCreatingVersion ? '创建新版本' : '上传新作品' }}
        <span v-if="isCreatingVersion" class="text-lg font-normal text-gray-500 dark:text-gray-400 ml-2">
          (基于现有图片)
        </span>
      </h1>
      
      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- File Upload -->
        <div class="card p-6">
          <h2 class="text-xl font-semibold mb-4">选择图片</h2>
          
          <div
            @drop="handleDrop"
            @dragover.prevent
            @dragenter.prevent
            class="border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg p-8 text-center hover:border-primary-500 transition-colors cursor-pointer"
            :class="{ 'border-primary-500 bg-primary-50 dark:bg-primary-900/10': isDragging }"
          >
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              @change="handleFileSelect"
              class="hidden"
            />
            
            <svg v-if="!preview" class="w-12 h-12 mx-auto text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path>
            </svg>
            
            <img v-if="preview" :src="preview" alt="Preview" class="max-h-64 mx-auto rounded" />
            
            <p class="mt-4 text-gray-600 dark:text-gray-400">
              拖拽图片到此处或
              <button type="button" @click="fileInput?.click()" class="text-primary-600 hover:text-primary-700 font-medium">
                点击选择
              </button>
            </p>
            
            <p class="text-sm text-gray-500 mt-2">
              支持 JPG, PNG, GIF, WebP 格式，最大 10MB
            </p>
          </div>
        </div>
        
        <!-- Prompt -->
        <div class="card p-6">
          <label class="block text-lg font-semibold mb-2">提示词 *</label>
          <textarea
            v-model="formData.prompt"
            required
            rows="4"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="描述您想要生成的图片内容..."
          ></textarea>
          <p class="text-sm text-gray-500 mt-2">{{ formData.prompt.length }}/5000</p>
        </div>
        
        <!-- Negative Prompt -->
        <div class="card p-6">
          <label class="block text-lg font-semibold mb-2">负面提示词</label>
          <textarea
            v-model="formData.negative_prompt"
            rows="3"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="描述不希望出现在图片中的内容..."
          ></textarea>
        </div>
        
        <!-- Model and Category -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="card p-6">
            <label class="block text-lg font-semibold mb-2">AI模型 *</label>
            <select
              v-model="formData.model_id"
              @change="onModelChange"
              required
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all hover:border-primary-300 dark:hover:border-primary-700"
            >
              <option value="">选择模型</option>
              <option v-for="model in models" :key="model.id" :value="model.id">
                {{ model.name }}
              </option>
              <option value="other">其他 (自定义)</option>
            </select>
            
            <!-- Custom Model Input -->
            <input
              v-if="formData.model_id === 'other'"
              v-model="formData.custom_model"
              type="text"
              placeholder="请输入模型名称"
              class="mt-3 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>
          
          <div class="card p-6">
            <label class="block text-lg font-semibold mb-2">分类 *</label>
            <select
              v-model="formData.category_id"
              @change="onCategoryChange"
              required
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all hover:border-primary-300 dark:hover:border-primary-700"
            >
              <option value="">选择分类</option>
              <option v-for="category in categories" :key="category.id" :value="category.id">
                {{ category.name }}
              </option>
              <option value="other">其他 (自定义)</option>
            </select>
            
            <!-- Custom Category Input -->
            <input
              v-if="formData.category_id === 'other'"
              v-model="formData.custom_category"
              type="text"
              placeholder="请输入分类名称"
              class="mt-3 w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              required
            />
          </div>
        </div>
        
        <!-- Tags -->
        <div class="card p-6">
          <label class="block text-lg font-semibold mb-2">标签</label>
          <div class="flex flex-wrap gap-2 mb-3" v-if="selectedTags.length > 0">
            <span
              v-for="tag in selectedTags"
              :key="tag.id"
              class="inline-flex items-center px-3 py-1 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 rounded-full text-sm font-medium shadow-sm"
            >
              {{ tag.name }}
              <button
                type="button"
                @click="removeTag(tag.id)"
                class="ml-2 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </span>
          </div>
          
          <div class="relative">
            <div class="flex gap-2">
              <input
                ref="tagInputRef"
                v-model="tagInput"
                @input="filterTags"
                @keydown.enter.prevent="handleTagEnter"
                @focus="showTagDropdown = true"
                @blur="hideTagDropdown"
                type="text"
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all hover:border-primary-300 dark:hover:border-primary-700"
                placeholder="输入标签名称,按回车或点击√添加..."
              />
              <button
                type="button"
                @click="handleTagEnter"
                :disabled="!tagInput.trim()"
                class="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                title="添加标签"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                </svg>
              </button>
            </div>
            
            <div
              v-if="showTagDropdown && filteredTags.length > 0"
              class="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-xl max-h-60 overflow-y-auto"
            >
              <button
                v-for="tag in filteredTags"
                :key="tag.id"
                type="button"
                @mousedown.prevent="addExistingTag(tag)"
                class="w-full px-4 py-2.5 text-left hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors border-b border-gray-100 dark:border-gray-700 last:border-b-0 flex items-center justify-between"
              >
                <span class="font-medium">{{ tag.name }}</span>
                <span v-if="tag.owner_id" class="text-xs text-gray-500 dark:text-gray-400">
                  {{ tag.is_public ? '公开' : '私有' }}
                </span>
              </button>
            </div>
          </div>
          
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-2">
            输入标签名称后按回车键或点击√添加。已有标签会显示联想提示。
          </p>
        </div>
        
        <!-- Public Toggle -->
        <div class="card p-6">
          <div class="flex items-center justify-between">
            <div>
              <label class="block text-lg font-semibold mb-1">公开作品</label>
              <p class="text-sm text-gray-500 dark:text-gray-400">
                公开后,其他用户可以在广场页面浏览您的作品
              </p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                v-model="formData.is_public"
                class="sr-only peer"
              />
              <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
            </label>
          </div>
        </div>
        
        <!-- Parameters -->
        <div class="card p-6">
          <div class="flex justify-between items-center mb-4">
            <label class="block text-lg font-semibold">额外参数</label>
            <button
              type="button"
              @click="addParameter"
              class="text-primary-600 hover:text-primary-700 font-medium"
            >
              + 添加参数
            </button>
          </div>
          
          <div class="space-y-3">
            <div
              v-for="(param, index) in formData.parameters"
              :key="index"
              class="flex gap-3"
            >
              <input
                v-model="param.key"
                type="text"
                placeholder="参数名 (如: Steps, CFG Scale)"
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500"
              />
              <input
                v-model="param.value"
                type="text"
                placeholder="参数值"
                class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 focus:ring-2 focus:ring-primary-500"
              />
              <button
                type="button"
                @click="removeParameter(index)"
                class="p-2 text-red-600 hover:text-red-700"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>
                </svg>
              </button>
            </div>
          </div>
        </div>
        
        <!-- Submit Button -->
        <div class="flex justify-end">
          <button
            type="submit"
            :disabled="isSubmitting || !selectedFile"
            class="btn-primary px-8 py-3 text-lg"
          >
            <span v-if="isSubmitting" class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
            {{ isSubmitting ? '上传中...' : '上传作品' }}
          </button>
        </div>
      </form>
    </main>
    
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from '../utils/axios';
import AppHeader from './AppHeader.vue';
import ToastContainer from './ToastContainer.vue';
import { useAuthStore } from '../stores/auth';
import { useToast } from '../composables/useToast';

const authStore = useAuthStore();
const { showToast } = useToast();

const selectedFile = ref<File | null>(null);
const preview = ref<string | null>(null);
const isDragging = ref(false);
const isSubmitting = ref(false);
const parentImageId = ref<number | null>(null);

const formData = ref({
  prompt: '',
  negative_prompt: '',
  model_id: '',
  category_id: '',
  custom_model: '',
  custom_category: '',
  is_public: false,
  parameters: [{ key: '', value: '' }]
});

const models = ref([]);
const categories = ref([]);
const tags = ref([]);
const selectedTags = ref([]);
const tagInput = ref('');
const showTagDropdown = ref(false);
const filteredTags = ref([]);

const fileInput = ref<HTMLInputElement>();
const tagInputRef = ref<HTMLInputElement>();

// Check if we're creating a new version
const isCreatingVersion = computed(() => !!parentImageId.value);

const handleDrop = (e: DragEvent) => {
  e.preventDefault();
  isDragging.value = false;
  
  const files = e.dataTransfer?.files;
  if (files && files.length > 0) {
    handleFile(files[0]);
  }
};

const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement;
  const files = target.files;
  if (files && files.length > 0) {
    handleFile(files[0]);
  }
};

const handleFile = (file: File) => {
  // Validate file
  if (!file.type.startsWith('image/')) {
    showToast('请选择图片文件', 'error');
    return;
  }
  
  if (file.size > 10 * 1024 * 1024) {
    showToast('文件大小不能超过 10MB', 'error');
    return;
  }
  
  selectedFile.value = file;
  
  // Create preview
  const reader = new FileReader();
  reader.onload = (e) => {
    preview.value = e.target?.result as string;
  };
  reader.readAsDataURL(file);
};

const onModelChange = () => {
  if (formData.value.model_id !== 'other') {
    formData.value.custom_model = '';
  }
};

const onCategoryChange = () => {
  if (formData.value.category_id !== 'other') {
    formData.value.custom_category = '';
  }
};

const filterTags = () => {
  if (!tagInput.value) {
    filteredTags.value = tags.value;
  } else {
    filteredTags.value = tags.value.filter(tag =>
      tag.name.toLowerCase().includes(tagInput.value.toLowerCase()) &&
      !selectedTags.value.some(t => t.id === tag.id)
    );
  }
};

const hideTagDropdown = () => {
  setTimeout(() => {
    showTagDropdown.value = false;
  }, 200);
};

const addExistingTag = (tag: any) => {
  if (!selectedTags.value.some(t => t.id === tag.id)) {
    selectedTags.value.push(tag);
  }
  tagInput.value = '';
  showTagDropdown.value = false;
  filterTags();
};

const handleTagEnter = async () => {
  const tagName = tagInput.value.trim();
  if (!tagName) return;
  
  // Check if tag already exists in filtered list
  const existingTag = tags.value.find(
    tag => tag.name.toLowerCase() === tagName.toLowerCase()
  );
  
  if (existingTag) {
    // Add existing tag
    addExistingTag(existingTag);
  } else {
    // Create new tag
    try {
      const response = await axios.post('/api/v1/tags', {
        name: tagName,
        is_public: false // Default to private for user-created tags
      });
      
      const newTag = response.data;
      tags.value.push(newTag);
      selectedTags.value.push(newTag);
      tagInput.value = '';
      filterTags();
      showToast('标签已创建并添加', 'success');
    } catch (error: any) {
      if (error.response?.data?.detail?.includes('already exists')) {
        showToast('标签已存在', 'error');
      } else {
        showToast('创建标签失败', 'error');
      }
    }
  }
};

const removeTag = (tagId: number) => {
  selectedTags.value = selectedTags.value.filter(t => t.id !== tagId);
};

const addParameter = () => {
  formData.value.parameters.push({ key: '', value: '' });
};

const removeParameter = (index: number) => {
  formData.value.parameters.splice(index, 1);
};

const handleSubmit = async () => {
  if (!selectedFile.value) {
    showToast('请选择要上传的图片', 'error');
    return;
  }
  
  // Validate model and category
  if (formData.value.model_id === 'other' && !formData.value.custom_model.trim()) {
    showToast('请输入自定义模型名称', 'error');
    return;
  }
  
  if (formData.value.category_id === 'other' && !formData.value.custom_category.trim()) {
    showToast('请输入自定义分类名称', 'error');
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const formDataToSend = new FormData();
    formDataToSend.append('file', selectedFile.value);
    formDataToSend.append('prompt', formData.value.prompt);
    formDataToSend.append('negative_prompt', formData.value.negative_prompt);
    formDataToSend.append('is_public', formData.value.is_public.toString());
    
    // Handle model
    if (formData.value.model_id === 'other') {
      formDataToSend.append('custom_model', formData.value.custom_model);
    } else {
      formDataToSend.append('model_id', formData.value.model_id.toString());
    }
    
    // Handle category
    if (formData.value.category_id === 'other') {
      formDataToSend.append('custom_category', formData.value.custom_category);
    } else {
      formDataToSend.append('category_id', formData.value.category_id.toString());
    }
    
    formDataToSend.append('tag_ids', selectedTags.value.map(t => t.id).join(','));

    // Add parent_image_id if creating a version
    if (parentImageId.value) {
      formDataToSend.append('parent_image_id', parentImageId.value.toString());
    }

    // Convert parameters to JSON
    const params: Record<string, string> = {};
    formData.value.parameters.forEach(param => {
      if (param.key && param.value) {
        params[param.key] = param.value;
      }
    });
    formDataToSend.append('parameters', JSON.stringify(params));

    const response = await axios.post('/api/v1/images', formDataToSend);
    
    showToast('上传成功！', 'success');
    window.location.href = '/';
  } catch (error: any) {
    showToast(error.response?.data?.detail || '上传失败', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    window.location.href = '/login';
    return;
  }

  // Fetch models and categories
  const [modelsRes, categoriesRes, tagsRes] = await Promise.all([
    axios.get('/api/v1/models'),
    axios.get('/api/v1/categories'),
    axios.get('/api/v1/tags')
  ]);

  models.value = modelsRes.data;
  categories.value = categoriesRes.data;
  tags.value = tagsRes.data;
  filteredTags.value = tags.value;

  // Check for query parameters for version creation
  const urlParams = new URLSearchParams(window.location.search);
  const parentIdParam = urlParams.get('parent_image_id');
  if (parentIdParam) {
    parentImageId.value = parseInt(parentIdParam);
  }

  // Pre-fill form data if provided
  const promptParam = urlParams.get('prompt');
  const negativePromptParam = urlParams.get('negative_prompt');
  const modelIdParam = urlParams.get('model_id');
  const categoryIdParam = urlParams.get('category_id');
  
  if (promptParam) formData.value.prompt = promptParam;
  if (negativePromptParam) formData.value.negative_prompt = negativePromptParam;
  if (modelIdParam) formData.value.model_id = modelIdParam;
  if (categoryIdParam) formData.value.category_id = categoryIdParam;

  // Pre-select tags if provided
  const tagsParam = urlParams.get('tags');
  if (tagsParam) {
    const tagIds = tagsParam.split(',').map(id => parseInt(id));
    const preselectedTags = tags.value.filter(tag => tagIds.includes(tag.id));
    selectedTags.value = preselectedTags;
  }
});
</script>