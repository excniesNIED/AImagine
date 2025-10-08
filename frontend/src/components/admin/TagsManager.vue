<template>
  <div class="space-y-6">
    <!-- Add Tag Form -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">添加标签</h2>
      <form @submit.prevent="addTag" class="flex gap-4">
        <input
          v-model="newTagName"
          type="text"
          placeholder="标签名称"
          class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500"
          required
        />
        <button type="submit" class="btn-primary">添加</button>
      </form>
    </div>

    <!-- Tags List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <div class="flex items-center justify-between">
          <h2 class="text-xl font-semibold">标签列表</h2>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索标签..."
            class="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-sm"
          />
        </div>
      </div>
      <div class="p-6">
        <div v-if="loading" class="flex justify-center py-8">
          <LoadingAnimation />
        </div>
        <div v-else-if="filteredTags.length === 0" class="text-center py-8 text-gray-500">
          {{ searchQuery ? '没有找到匹配的标签' : '暂无标签' }}
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="tag in filteredTags"
            :key="tag.id"
            class="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div>
              <span class="font-medium">{{ tag.name }}</span>
              <span class="text-sm text-gray-500 ml-2">({{ tag.image_count || 0 }} 张图片)</span>
            </div>
            <div class="flex gap-2">
              <button
                @click="editTag(tag)"
                class="px-2 py-1 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
              >
                编辑
              </button>
              <button
                @click="deleteTag(tag.id)"
                class="px-2 py-1 text-xs bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Merge Tags Modal -->
    <div v-if="showMergeModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">合并标签</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          将 <strong>{{ selectedTag?.name }}</strong> 合并到：
        </p>
        <DropdownSelect
          v-model="targetTagId"
          :options="mergeTagOptions"
          placeholder="选择目标标签"
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
        <h3 class="text-xl font-semibold mb-4">编辑标签</h3>
        <input
          v-model="editTagName"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 mb-4"
          placeholder="标签名称"
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
import { useAuthStore } from '../../stores/auth';
import LoadingAnimation from '../LoadingAnimation.vue';
import DropdownSelect from '../DropdownSelect.vue';

const toast = useToast();
const authStore = useAuthStore();

interface Tag {
  id: number;
  name: string;
  image_count?: number;
}

const tags = ref<Tag[]>([]);
const loading = ref(true);
const newTagName = ref('');
const searchQuery = ref('');

// Merge modal
const showMergeModal = ref(false);
const selectedTag = ref<Tag | null>(null);
const targetTagId = ref<number | null>(null);

// Edit modal
const showEditModal = ref(false);
const editTagName = ref('');
const editingTagId = ref<number | null>(null);
const mergeTagOptions = computed(() => {
  const list = tags.value.filter(t => t.id !== selectedTag.value?.id);
  const opts = list.map(t => ({ value: t.id, label: `${t.name} (${t.image_count || 0} 张图片)` }));
  return [{ value: '', label: '选择目标标签' }, ...opts];
});

const filteredTags = computed(() => {
  if (!searchQuery.value) return tags.value;
  return tags.value.filter(tag =>
    tag.name.toLowerCase().includes(searchQuery.value.toLowerCase())
  );
});

const fetchTags = async () => {
  try {
    loading.value = true;
    const response = await axios.get('/api/v1/tags/', { params: { include_count: true } });
    tags.value = response.data;
  } catch (error) {
    toast.error('获取标签列表失败');
    console.error('Failed to fetch tags:', error);
  } finally {
    loading.value = false;
  }
};

const addTag = async () => {
  try {
    await axios.post('/api/v1/tags/', { name: newTagName.value });
    toast.success('标签添加成功');
    newTagName.value = '';
    fetchTags();
  } catch (error: any) {
    console.error('Failed to add tag:', error);

    if (error.response?.status === 401) {
      toast.error('登录已过期，请重新登录');
      authStore.logout();
      setTimeout(() => {
        window.location.href = '/login';
      }, 1000);
    } else {
      toast.error('添加标签失败');
    }
  }
};

const editTag = (tag: Tag) => {
  editingTagId.value = tag.id;
  editTagName.value = tag.name;
  showEditModal.value = true;
};

const confirmEdit = async () => {
  if (!editingTagId.value) return;

  try {
    await axios.put(`/api/v1/tags/${editingTagId.value}/`, {
      name: editTagName.value
    });
    toast.success('标签更新成功');
    showEditModal.value = false;
    fetchTags();
  } catch (error) {
    toast.error('更新标签失败');
    console.error('Failed to update tag:', error);
  }
};

const deleteTag = async (tagId: number) => {
  if (!confirm('确定要删除这个标签吗？')) return;

  try {
    await axios.delete(`/api/v1/tags/${tagId}/`);
    toast.success('标签删除成功');
    fetchTags();
  } catch (error) {
    toast.error('删除标签失败');
    console.error('Failed to delete tag:', error);
  }
};

onMounted(() => {
  fetchTags();
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