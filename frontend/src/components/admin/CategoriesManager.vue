<template>
  <div class="space-y-6">
    <!-- Add Category Form -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">添加分类</h2>
      <form @submit.prevent="addCategory" class="flex gap-4">
        <input
          v-model="newCategoryName"
          type="text"
          placeholder="分类名称"
          class="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500"
          required
        />
        <button type="submit" class="btn-primary">添加</button>
      </form>
    </div>

    <!-- Categories List -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h2 class="text-xl font-semibold">分类列表</h2>
      </div>
      <div class="p-6">
        <div v-if="loading" class="flex justify-center py-8">
          <LoadingAnimation />
        </div>
        <div v-else-if="categories.length === 0" class="text-center py-8 text-gray-500">
          暂无分类
        </div>
        <div v-else class="space-y-2">
          <div
            v-for="category in categories"
            :key="category.id"
            class="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <div class="flex items-center gap-4">
              <span class="font-medium">{{ category.name }}</span>
              <span class="text-sm text-gray-500">{{ category.image_count || 0 }} 张图片</span>
            </div>
            <div class="flex gap-2">
              <button
                @click="editCategory(category)"
                class="px-3 py-1 text-sm bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
              >
                编辑
              </button>
              <button
                @click="deleteCategory(category.id)"
                class="px-3 py-1 text-sm bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 rounded hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Merge Categories Modal -->
    <div v-if="showMergeModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">合并分类</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          将 <strong>{{ selectedCategory?.name }}</strong> 合并到：
        </p>
        <select
          v-model="targetCategoryId"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 mb-4"
        >
          <option value="">选择目标分类</option>
          <option
            v-for="cat in categories.filter(c => c.id !== selectedCategory?.id)"
            :key="cat.id"
            :value="cat.id"
          >
            {{ cat.name }}
          </option>
        </select>
        <div class="flex justify-end gap-2">
          <button @click="showMergeModal = false" class="btn-secondary">取消</button>
          <button @click="confirmMerge" class="btn-primary">确认合并</button>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">编辑分类</h3>
        <input
          v-model="editCategoryName"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 mb-4"
          placeholder="分类名称"
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
import { ref, onMounted } from 'vue';
import axios from '../../utils/axios';
import { useToast } from '../../composables/useToast';
import LoadingAnimation from '../LoadingAnimation.vue';

const toast = useToast();

interface Category {
  id: number;
  name: string;
  image_count?: number;
}

const categories = ref<Category[]>([]);
const loading = ref(true);
const newCategoryName = ref('');

// Merge modal
const showMergeModal = ref(false);
const selectedCategory = ref<Category | null>(null);
const targetCategoryId = ref<number | null>(null);

// Edit modal
const showEditModal = ref(false);
const editCategoryName = ref('');
const editingCategoryId = ref<number | null>(null);

const fetchCategories = async () => {
  try {
    loading.value = true;
    const response = await axios.get('/api/v1/categories');
    categories.value = response.data;
  } catch (error) {
    toast.error('获取分类列表失败');
    console.error('Failed to fetch categories:', error);
  } finally {
    loading.value = false;
  }
};

const addCategory = async () => {
  try {
    await axios.post('/api/v1/categories', { name: newCategoryName.value });
    toast.success('分类添加成功');
    newCategoryName.value = '';
    fetchCategories();
  } catch (error) {
    toast.error('添加分类失败');
    console.error('Failed to add category:', error);
  }
};

const editCategory = (category: Category) => {
  editingCategoryId.value = category.id;
  editCategoryName.value = category.name;
  showEditModal.value = true;
};

const confirmEdit = async () => {
  if (!editingCategoryId.value) return;

  try {
    await axios.put(`/api/v1/categories/${editingCategoryId.value}`, {
      name: editCategoryName.value
    });
    toast.success('分类更新成功');
    showEditModal.value = false;
    fetchCategories();
  } catch (error) {
    toast.error('更新分类失败');
    console.error('Failed to update category:', error);
  }
};

const deleteCategory = async (categoryId: number) => {
  if (!confirm('确定要删除这个分类吗？')) return;

  try {
    await axios.delete(`/api/v1/categories/${categoryId}`);
    toast.success('分类删除成功');
    fetchCategories();
  } catch (error) {
    toast.error('删除分类失败');
    console.error('Failed to delete category:', error);
  }
};

onMounted(() => {
  fetchCategories();
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