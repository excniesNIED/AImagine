<template>
  <div class="space-y-6">
    <!-- Add Model Form -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">添加模型</h2>
      <form @submit.prevent="addModel" class="flex gap-4">
        <input
          v-model="newModelName"
          type="text"
          placeholder="模型名称"
          class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500"
          required
        />
        <button type="submit" class="btn-primary">添加</button>
      </form>
    </div>

    <!-- Models List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold">模型列表</h2>
      </div>
      <div class="p-6">
        <div v-if="loading" class="flex justify-center py-8">
          <LoadingAnimation />
        </div>
        <div v-else-if="models.length === 0" class="text-center py-8 text-gray-500">
          暂无模型
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="model in models"
            :key="model.id"
            class="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <div class="flex items-center gap-4">
              <span class="font-medium">{{ model.name }}</span>
              <span class="text-sm text-gray-500">{{ model.image_count || 0 }} 张图片</span>
            </div>
            <div class="flex gap-2">
              <button
                @click="editModel(model)"
                class="px-3 py-1 text-sm bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
              >
                编辑
              </button>
              <button
                @click="deleteModel(model.id)"
                class="px-3 py-1 text-sm bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Merge Models Modal -->
    <div v-if="showMergeModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">合并模型</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          将 <strong>{{ selectedModel?.name }}</strong> 合并到：
        </p>
        <DropdownSelect
          v-model="targetModelId"
          :options="mergeModelOptions"
          placeholder="选择目标模型"
        />
        <div class="flex justify-end gap-2">
          <button @click="showMergeModal = false" class="btn-secondary">取消</button>
          <button @click="confirmMerge" class="btn-primary">确认合并</button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">编辑模型</h3>
        <input
          v-model="editModelName"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 mb-4"
          placeholder="模型名称"
        />
        <div class="flex justify-end gap-2">
          <button @click="showEditModal = false" class="btn-secondary">取消</button>
          <button @click="confirmEdit" class="btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from '../../utils/axios';
import { useToast } from '../../composables/useToast';
import LoadingAnimation from '../LoadingAnimation.vue';
import DropdownSelect from '../DropdownSelect.vue';

const toast = useToast();

interface Model {
  id: number;
  name: string;
  image_count?: number;
}

const models = ref<Model[]>([]);
const loading = ref(true);
const newModelName = ref('');

// Merge modal
const showMergeModal = ref(false);
const selectedModel = ref<Model | null>(null);
const targetModelId = ref<number | null>(null);

// Edit modal
const showEditModal = ref(false);
const editModelName = ref('');
const editingModelId = ref<number | null>(null);

const mergeModelOptions = computed(() => {
  const list = models.value.filter(m => m.id !== selectedModel.value?.id);
  const opts = list.map(m => ({ value: m.id, label: `${m.name} (${m.image_count || 0} 张图片)` }));
  return [{ value: '', label: '选择目标模型' }, ...opts];
});

const fetchModels = async () => {
  try {
    loading.value = true;
    const response = await axios.get('/api/v1/models');
    models.value = response.data;
  } catch (error) {
    toast.error('获取模型列表失败');
    console.error('Failed to fetch models:', error);
  } finally {
    loading.value = false;
  }
};

const addModel = async () => {
  try {
    await axios.post('/api/v1/models', { name: newModelName.value });
    toast.success('模型添加成功');
    newModelName.value = '';
    fetchModels();
  } catch (error) {
    toast.error('添加模型失败');
    console.error('Failed to add model:', error);
  }
};

const editModel = (model: Model) => {
  editingModelId.value = model.id;
  editModelName.value = model.name;
  showEditModal.value = true;
};

const confirmEdit = async () => {
  if (!editingModelId.value) return;

  try {
    await axios.put(`/api/v1/models/${editingModelId.value}`, {
      name: editModelName.value
    });
    toast.success('模型更新成功');
    showEditModal.value = false;
    fetchModels();
  } catch (error) {
    toast.error('更新模型失败');
    console.error('Failed to update model:', error);
  }
};

const deleteModel = async (modelId: number) => {
  if (!confirm('确定要删除这个模型吗？')) return;

  try {
    await axios.delete(`/api/v1/models/${modelId}`);
    toast.success('模型删除成功');
    fetchModels();
  } catch (error) {
    toast.error('删除模型失败');
    console.error('Failed to delete model:', error);
  }
};

onMounted(() => {
  fetchModels();
});
</script>

<style scoped>
.btn-primary {
  @apply px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors;
}

.btn-secondary {
  @apply px-4 py-2 bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors;
}
</style>