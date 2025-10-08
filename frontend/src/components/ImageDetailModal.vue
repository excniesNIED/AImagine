<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 overflow-y-auto" @click.self="$emit('close')">
      <div class="flex min-h-full items-center justify-center p-4">
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-75"></div>
        
        <!-- Modal -->
        <div class="relative w-full max-w-6xl max-h-[90vh] overflow-hidden bg-white dark:bg-gray-800 rounded-xl shadow-2xl">
          <!-- Close button -->
          <button
            @click="$emit('close')"
            class="absolute top-4 right-4 z-10 p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 bg-white dark:bg-gray-800 rounded-full"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
          
          <div class="flex h-full">
            <!-- Image Section -->
                <div class="flex-1 bg-black flex items-center justify-center p-8">
              <img
                :src="currentImage.alist_url"
                :alt="currentImage.prompt"
                class="max-w-full max-h-full object-contain"
              />
            </div>
            
            <!-- Details Section -->
            <div class="w-full md:w-96 flex flex-col h-full">
              <div class="flex-1 overflow-y-auto p-6 space-y-6">
                <!-- Title -->
                <div>
                  <h2 class="text-2xl font-bold mb-2">作品详情</h2>
                  <div class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
                    <span>{{ currentImage.model?.name || currentImage.custom_model || '未知模型' }}</span>
                    <span>•</span>
                    <span>{{ formatDate(currentImage.created_at) }}</span>
                  </div>
                </div>

                <!-- Prompt -->
                <div>
                  <h3 class="text-lg font-semibold mb-2">提示词</h3>
                  <div class="relative">
                    <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ currentImage.prompt }}</p>
                    <button
                      @click="copyToClipboard(currentImage.prompt)"
                      class="absolute top-0 right-0 p-2 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                    >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"></path>
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Negative Prompt -->
                <div v-if="currentImage.negative_prompt">
                  <h3 class="text-lg font-semibold mb-2">负面提示词</h3>
                  <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">{{ currentImage.negative_prompt }}</p>
                </div>

                <!-- Category and Tags -->
                <div>
                  <h3 class="text-lg font-semibold mb-2">分类与标签</h3>
                  <div class="space-y-2">
                    <span class="inline-block px-3 py-1 bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-200 rounded-full text-sm">
                      {{ currentImage.category?.name || currentImage.custom_category || '未分类' }}
                    </span>
                    <span
                      v-for="tag in (currentImage.tags || [])"
                      :key="tag.id"
                      class="inline-block px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-full text-sm ml-2"
                    >
                      {{ tag.name }}
                    </span>
                  </div>
                </div>

                <!-- Parameters -->
                <div v-if="currentImage.parameters && currentImage.parameters.length">
                  <h3 class="text-lg font-semibold mb-2">参数</h3>
                  <dl class="grid grid-cols-2 gap-2 text-sm">
                    <div v-for="param in currentImage.parameters" :key="param.key">
                      <dt class="font-medium text-gray-600 dark:text-gray-400">{{ param.key }}</dt>
                      <dd class="text-gray-900 dark:text-gray-100">{{ param.value }}</dd>
                    </div>
                  </dl>
                </div>
                
                <!-- Version History -->
                <div>
                  <div class="flex items-center justify-between mb-2">
                    <h3 class="text-lg font-semibold">版本历史</h3>
                    <button
                      @click="toggleVersionHistory"
                      class="text-sm text-primary-600 dark:text-primary-400 hover:underline"
                    >
                      {{ showVersions ? '收起' : '展开' }}
                    </button>
                  </div>

                  <div v-if="showVersions">
                    <div v-if="loadingVersions" class="flex justify-center py-4">
                      <LoadingAnimation />
                    </div>

                    <div v-else-if="versions.length <= 1" class="text-gray-500 dark:text-gray-400 text-sm">
                      这是初始版本
                    </div>

                    <div v-else class="space-y-2">
                      <div
                        v-for="(version, index) in versions"
                        :key="version.id"
                        @click="viewVersion(version)"
                        :class="[
                          'flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors',
                          version.id === currentImage.id
                            ? 'bg-primary-100 dark:bg-primary-900/30 border border-primary-300 dark:border-primary-700'
                            : 'hover:bg-gray-100 dark:hover:bg-gray-700'
                        ]"
                      >
                        <img
                          :src="version.alist_url"
                          :alt="version.prompt"
                          class="w-16 h-16 object-cover rounded"
                        />

                        <div class="flex-1 min-w-0">
                          <p class="text-sm font-medium truncate">
                            {{ version.id === currentImage.id ? '当前版本' : `版本 ${index + 1}` }}
                          </p>
                          <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
                            {{ version.prompt.substring(0, 50) }}...
                          </p>
                          <p class="text-xs text-gray-400 dark:text-gray-500">
                            {{ formatDate(version.created_at) }}
                          </p>
                        </div>

                        <div v-if="version.id !== currentImage.id" class="flex gap-1">
                          <button
                            @click.stop="createVersionFrom(version)"
                            class="p-1 text-gray-500 hover:text-primary-600 dark:hover:text-primary-400"
                            title="基于此版本创作"
                          >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                            </svg>
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Actions -->
              <div class="border-t border-gray-200 dark:border-gray-700 p-4 space-y-2">
                <button
                  v-if="canEdit"
                  @click="editImage"
                  class="w-full btn-primary"
                >
                  编辑
                </button>
                <button
                  @click="createNewVersion"
                  class="w-full btn-secondary"
                >
                  基于此图创作
                </button>
                <button
                  v-if="canDelete"
                  @click="deleteImage"
                  class="w-full px-4 py-2 border border-red-300 dark:border-red-600 text-sm font-medium rounded-md text-red-700 dark:text-red-200 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue';
import axios from '../utils/axios';
import { useAuthStore } from '../stores/auth';
import { useToast } from '../composables/useToast';
import LoadingAnimation from './LoadingAnimation.vue';

interface Image {
  id: number;
  prompt: string;
  negative_prompt?: string;
  alist_url: string;
  created_at: string;
  owner_id: number;
  model: { id: number; name: string };
  category: { id: number; name: string };
  tags: { id: number; name: string }[];
  parameters?: { key: string; value: string }[];
}

interface Props {
  image: Image;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  close: [];
  update: [image: Image];
  delete: [id: number];
}>();

const authStore = useAuthStore();
const { showToast } = useToast();

// Version history state
const showVersions = ref(false);
const versions = ref<Image[]>([]);
const loadingVersions = ref(false);
const currentImage = ref<Image>(props.image);

const canEdit = computed(() => {
  return authStore.user?.id === props.image.owner_id || authStore.isAdmin;
});

const canDelete = computed(() => {
  return authStore.user?.id === props.image.owner_id || authStore.isAdmin;
});

// Watch for image changes
watch(() => props.image, (newImage) => {
  currentImage.value = newImage;
  if (showVersions.value) {
    fetchVersions();
  }
});

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleString('zh-CN');
};

const copyToClipboard = async (text: string) => {
  try {
    await navigator.clipboard.writeText(text);
    showToast('已复制到剪贴板', 'success');
  } catch (error) {
    showToast('复制失败', 'error');
  }
};

const toggleVersionHistory = () => {
  showVersions.value = !showVersions.value;
  if (showVersions.value && versions.value.length === 0) {
    fetchVersions();
  }
};

const fetchVersions = async () => {
  try {
    loadingVersions.value = true;
    const response = await axios.get(`/api/v1/images/${props.image.id}/versions`);
    versions.value = response.data;
  } catch (error) {
    console.error('Failed to fetch versions:', error);
    showToast('获取版本历史失败', 'error');
  } finally {
    loadingVersions.value = false;
  }
};

const viewVersion = (version: Image) => {
  if (version.id !== props.image.id) {
    currentImage.value = version;
    emit('update', version);
  }
};

const createVersionFrom = async (version: Image) => {
  try {
    const response = await axios.post(`/api/v1/images/${version.id}/iterate`);
    const parentData = response.data;

    // Navigate to upload page with pre-filled data
    const params = new URLSearchParams({
      parent_id: version.id.toString(),
      prompt: parentData.prompt,
      negative_prompt: parentData.negative_prompt || '',
      model_id: parentData.model_id.toString(),
      category_id: parentData.category_id.toString(),
      tags: parentData.tags?.map((t: any) => t.id).join(',') || ''
    });
    window.location.href = `/upload?${params.toString()}`;
  } catch (error) {
    showToast('无法创建新版本', 'error');
  }
};

const editImage = () => {
  // TODO: Implement edit modal
  showToast('编辑功能开发中', 'info');
};

const createNewVersion = async () => {
  try {
    const response = await axios.post(`/api/v1/images/${props.image.id}/iterate`);
    const parentData = response.data;

    // Navigate to upload page with pre-filled data
    const params = new URLSearchParams({
      parent_id: props.image.id.toString(),
      prompt: parentData.prompt,
      negative_prompt: parentData.negative_prompt || '',
      model_id: parentData.model_id.toString(),
      category_id: parentData.category_id.toString(),
      tags: parentData.tags?.map((t: any) => t.id).join(',') || ''
    });
    window.location.href = `/upload?${params.toString()}`;
  } catch (error) {
    showToast('无法创建新版本', 'error');
  }
};

const deleteImage = async () => {
  if (!confirm('确定要删除这张图片吗？如果有子版本，需要先删除所有子版本。')) return;

  try {
    await axios.delete(`/api/v1/images/${props.image.id}`);
    showToast('删除成功', 'success');
    emit('delete', props.image.id);
  } catch (error: any) {
    if (error.response?.status === 400 && error.response?.data?.detail) {
      showToast(error.response.data.detail, 'error');
    } else {
      showToast('删除失败', 'error');
    }
  }
};
</script>