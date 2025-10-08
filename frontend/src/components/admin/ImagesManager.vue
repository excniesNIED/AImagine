<template>
  <div class="space-y-6">
    <!-- Filters & Actions -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <input v-model="search" type="text" placeholder="搜索提示词..." class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
        <DropdownSelect v-model="filters.categoryIds" :options="categoryOptions" placeholder="按分类筛选" multiple clearable />
        <DropdownSelect v-model="filters.modelIds" :options="modelOptions" placeholder="按模型筛选" multiple clearable />
        <DropdownSelect v-model="filters.tagIds" :options="tagOptions" placeholder="按标签筛选" multiple clearable />
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        <button @click="fetchImages" class="btn-primary">刷新</button>
        <button @click="openReassignCategory" :disabled="!hasSelection" class="btn-secondary">批量改分类</button>
        <button @click="openReassignModel" :disabled="!hasSelection" class="btn-secondary">批量改模型</button>
        <button @click="openAttachTags" :disabled="!hasSelection" class="btn-secondary">批量加标签</button>
        <button @click="openDetachTags" :disabled="!hasSelection" class="btn-secondary">批量移除标签</button>
        <button @click="confirmBulkDelete" :disabled="!hasSelection" class="px-4 py-2 border border-red-300 dark:border-red-600 text-sm font-medium rounded-md text-red-700 dark:text-red-200 bg-white dark:bg-gray-800 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">批量删除</button>
      </div>
      <div class="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        <DropdownSelect v-model="filters.paramKeys" :options="parameterKeyOptions" placeholder="参数键（多选）" multiple clearable />
        <DropdownSelect v-model="filters.paramFilterKey" :options="parameterKeyOptions" placeholder="参数键（精确匹配）" clearable />
        <input v-model="filters.paramFilterValue" type="text" placeholder="参数值（可留空表示仅存在键）" class="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
      </div>
    </div>

    <!-- Images Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h2 class="text-xl font-semibold">作品列表</h2>
        <div class="text-sm text-gray-500">共 {{ total }} 项</div>
      </div>

      <div v-if="loading" class="flex justify-center py-10">
        <LoadingAnimation />
      </div>
      <div v-else>
        <div v-if="items.length === 0" class="text-center py-10 text-gray-500">暂无数据</div>
        <table v-else class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th class="px-4 py-3">
                <input type="checkbox" :checked="allSelected" @change="toggleSelectAll" />
              </th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">预览</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">提示词</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">分类</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">模型</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">标签</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">公开</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="img in items" :key="img.id">
              <td class="px-4 py-3">
                <input type="checkbox" :checked="selectedIds.has(img.id)" @change="toggleSelect(img.id)" />
              </td>
              <td class="px-4 py-3">
                <img :src="img.alist_url" :alt="img.prompt" class="w-16 h-16 object-cover rounded" />
              </td>
              <td class="px-4 py-3 max-w-md">
                <div class="line-clamp-2 text-sm">{{ img.prompt }}</div>
                <div class="text-xs text-gray-500">{{ formatDate(img.created_at) }}</div>
              </td>
              <td class="px-4 py-3 text-sm">{{ img.category?.name || img.custom_category || '未分类' }}</td>
              <td class="px-4 py-3 text-sm">{{ img.model?.name || img.custom_model || '未知模型' }}</td>
              <td class="px-4 py-3 text-sm">
                <span v-for="t in img.tags || []" :key="t.id" class="inline-block px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs mr-1 mb-1">{{ t.name }}</span>
              </td>
              <td class="px-4 py-3">
                <span :class="img.is_public ? 'text-green-600' : 'text-gray-400'" class="text-xs font-medium">{{ img.is_public ? '是' : '否' }}</span>
              </td>
              <td class="px-4 py-3 text-right">
                <button @click="openEdit(img)" class="px-2 py-1 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors">编辑</button>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="p-4 flex items-center justify-between">
          <div class="text-sm text-gray-500">已选 {{ selectedIds.size }} 项</div>
          <div class="flex items-center gap-2">
            <button :disabled="page===1" @click="prevPage" class="btn-secondary">上一页</button>
            <span class="text-sm">第 {{ page }} / {{ totalPages }} 页</span>
            <button :disabled="page===totalPages" @click="nextPage" class="btn-secondary">下一页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEdit" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl">
        <h3 class="text-xl font-semibold mb-4">编辑作品</h3>
        <div class="space-y-4">
          <textarea v-model="editForm.prompt" rows="4" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" placeholder="提示词"></textarea>
          <textarea v-model="editForm.negative_prompt" rows="3" class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" placeholder="负面提示词"></textarea>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
            <DropdownSelect v-model="editForm.category_id" :options="categoryOptions" placeholder="分类" />
            <DropdownSelect v-model="editForm.model_id" :options="modelOptions" placeholder="模型" />
            <DropdownSelect v-model="editForm.tags" :options="tagOptions" placeholder="标签" multiple clearable />
          </div>
          <label class="inline-flex items-center gap-2 text-sm">
            <input type="checkbox" v-model="editForm.is_public" /> 公开显示
          </label>
        </div>
        <div class="mt-6 flex justify-end gap-2">
          <button @click="showEdit=false" class="btn-secondary">取消</button>
          <button @click="saveEdit" class="btn-primary">保存</button>
        </div>
      </div>
    </div>

    <!-- Modals: Bulk Ops -->
    <div v-if="modal.reassignCategory" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">批量修改分类</h3>
        <DropdownSelect v-model="bulk.targetCategoryId" :options="categoryOptions" placeholder="选择目标分类" />
        <div class="mt-4 flex justify-end gap-2">
          <button @click="modal.reassignCategory=false" class="btn-secondary">取消</button>
          <button @click="doReassignCategory" class="btn-primary">确定</button>
        </div>
      </div>
    </div>

    <div v-if="modal.reassignModel" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">批量修改模型</h3>
        <DropdownSelect v-model="bulk.targetModelId" :options="modelOptions" placeholder="选择目标模型" />
        <div class="mt-4 flex justify-end gap-2">
          <button @click="modal.reassignModel=false" class="btn-secondary">取消</button>
          <button @click="doReassignModel" class="btn-primary">确定</button>
        </div>
      </div>
    </div>

    <div v-if="modal.attachTags" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">批量添加标签</h3>
        <DropdownSelect v-model="bulk.tagIds" :options="tagOptions" placeholder="选择标签" multiple clearable />
        <div class="mt-4 flex justify-end gap-2">
          <button @click="modal.attachTags=false" class="btn-secondary">取消</button>
          <button @click="doAttachTags" class="btn-primary">确定</button>
        </div>
      </div>
    </div>

    <div v-if="modal.detachTags" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4">批量移除标签</h3>
        <DropdownSelect v-model="bulk.tagIds" :options="tagOptions" placeholder="选择标签" multiple clearable />
        <div class="mt-4 flex justify-end gap-2">
          <button @click="modal.detachTags=false" class="btn-secondary">取消</button>
          <button @click="doDetachTags" class="btn-primary">确定</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import axios from '../../utils/axios';
import { useToast } from '../../composables/useToast';
import LoadingAnimation from '../LoadingAnimation.vue';
import DropdownSelect from '../DropdownSelect.vue';

const toast = useToast();

interface ImageItem {
  id: number;
  prompt: string;
  negative_prompt?: string;
  alist_url: string;
  created_at: string;
  is_public: boolean;
  custom_model?: string;
  custom_category?: string;
  model?: { id: number; name: string } | null;
  model_id?: number | null;
  category?: { id: number; name: string } | null;
  category_id?: number | null;
  tags?: { id: number; name: string }[];
}

interface ListResponse {
  items: ImageItem[];
  total: number;
  page: number;
  size: number;
}

const loading = ref(false);
const items = ref<ImageItem[]>([]);
const total = ref(0);
const page = ref(1);
const size = ref(20);

const search = ref('');
const filters = ref<{
  categoryIds: Array<number | string> | [];
  modelIds: Array<number | string> | [];
  tagIds: Array<number | string> | [];
  paramKeys: Array<string | number> | [];
  paramFilterKey: string | '';
  paramFilterValue: string | '';
}>({ categoryIds: [], modelIds: [], tagIds: [], paramKeys: [], paramFilterKey: '', paramFilterValue: '' });

const selectedIds = ref<Set<number>>(new Set());
const hasSelection = computed(() => selectedIds.value.size > 0);
const allSelected = computed(() => items.value.length > 0 && items.value.every(i => selectedIds.value.has(i.id)));

const categories = ref<{ id: number; name: string }[]>([]);
const models = ref<{ id: number; name: string }[]>([]);
const tags = ref<{ id: number; name: string }[]>([]);

const categoryOptions = computed(() => categories.value.map(c => ({ value: c.id, label: c.name })));
const modelOptions = computed(() => models.value.map(m => ({ value: m.id, label: m.name })));
const tagOptions = computed(() => tags.value.map(t => ({ value: t.id, label: t.name })));

// Parameter keys derived from currently loaded images
const parameterKeyOptions = computed(() => {
  const keys = new Set<string>();
  items.value.forEach(img => {
    (img.tags || []); // no-op to avoid unused var lint
  });
  items.value.forEach(img => {
    (img as any).parameters?.forEach((p: any) => { if (p?.key) keys.add(p.key); });
  });
  return Array.from(keys).map(k => ({ value: k, label: k }));
});

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / size.value)));

const fetchFilters = async () => {
  try {
    const [cats, mods, tgs] = await Promise.all([
      axios.get('/api/v1/categories/'),
      axios.get('/api/v1/models/'),
      axios.get('/api/v1/tags/')
    ]);
    categories.value = cats.data || [];
    models.value = mods.data || [];
    tags.value = tgs.data || [];
  } catch (e) {
    // ignore
  }
};

const fetchImages = async () => {
  try {
    loading.value = true;
    const params: any = {
      skip: (page.value - 1) * size.value,
      limit: size.value,
    };
    if (search.value) params.search = search.value;
    if ((filters.value.categoryIds as any[]).length) params.category_ids = (filters.value.categoryIds as any[]).join(',');
    if ((filters.value.modelIds as any[]).length) params.model_ids = (filters.value.modelIds as any[]).join(',');
    if ((filters.value.tagIds as any[]).length) params.tag_ids = (filters.value.tagIds as any[]).join(',');
    if ((filters.value.paramKeys as any[]).length) params.param_keys = (filters.value.paramKeys as any[]).join(',');
    if (filters.value.paramFilterKey) {
      const kv: Record<string, string> = {};
      kv[filters.value.paramFilterKey] = (filters.value.paramFilterValue || '').toString();
      params.param_filters = JSON.stringify(kv);
    }

    const res = await axios.get('/api/v1/admin/images', { params });
    const data: ListResponse = res.data;
    items.value = data.items || [];
    total.value = data.total || 0;
  } catch (e) {
    toast.error('获取作品列表失败');
  } finally {
    loading.value = false;
  }
};

const toggleSelect = (id: number) => {
  const s = new Set(selectedIds.value);
  if (s.has(id)) s.delete(id); else s.add(id);
  selectedIds.value = s;
};

const toggleSelectAll = () => {
  if (allSelected.value) {
    selectedIds.value = new Set();
  } else {
    selectedIds.value = new Set(items.value.map(i => i.id));
  }
};

const prevPage = () => { if (page.value > 1) { page.value -= 1; fetchImages(); selectedIds.value = new Set(); } };
const nextPage = () => { if (page.value < totalPages.value) { page.value += 1; fetchImages(); selectedIds.value = new Set(); } };

const formatDate = (s: string) => new Date(s).toLocaleString('zh-CN');

// Edit single image
const showEdit = ref(false);
const editing = ref<ImageItem | null>(null);
const editForm = ref<any>({ prompt: '', negative_prompt: '', category_id: '', model_id: '', tags: [], is_public: false });

const openEdit = (img: ImageItem) => {
  editing.value = img;
  editForm.value = {
    prompt: img.prompt,
    negative_prompt: img.negative_prompt || '',
    category_id: img.category?.id || '',
    model_id: img.model?.id || '',
    tags: (img.tags || []).map(t => t.id),
    is_public: !!img.is_public
  };
  showEdit.value = true;
};

const saveEdit = async () => {
  if (!editing.value) return;
  try {
    await axios.put(`/api/v1/images/${editing.value.id}`, {
      prompt: editForm.value.prompt,
      negative_prompt: editForm.value.negative_prompt || null,
      category_id: editForm.value.category_id || null,
      model_id: editForm.value.model_id || null,
      tags: editForm.value.tags || [],
      is_public: !!editForm.value.is_public
    });
    toast.success('更新成功');
    showEdit.value = false;
    fetchImages();
  } catch (e) {
    toast.error('更新失败');
  }
};

// Bulk operations
const modal = ref({ reassignCategory: false, reassignModel: false, attachTags: false, detachTags: false });
const bulk = ref<{ targetCategoryId: number | '' | null; targetModelId: number | '' | null; tagIds: Array<number | string> | [] }>({ targetCategoryId: '', targetModelId: '', tagIds: [] });

const openReassignCategory = () => { modal.value.reassignCategory = true; };
const openReassignModel = () => { modal.value.reassignModel = true; };
const openAttachTags = () => { modal.value.attachTags = true; };
const openDetachTags = () => { modal.value.detachTags = true; };

const doReassignCategory = async () => {
  try {
    await axios.post('/api/v1/admin/images/bulk/reassign-category', {
      source_category_id: null,
      target_category_id: bulk.value.targetCategoryId,
      image_ids: Array.from(selectedIds.value)
    });
    toast.success('分类已更新');
    modal.value.reassignCategory = false;
    fetchImages();
  } catch (e) {
    toast.error('批量修改分类失败');
  }
};

const doReassignModel = async () => {
  try {
    await axios.post('/api/v1/admin/images/bulk/reassign-model', {
      source_model_id: null,
      target_model_id: bulk.value.targetModelId,
      image_ids: Array.from(selectedIds.value)
    });
    toast.success('模型已更新');
    modal.value.reassignModel = false;
    fetchImages();
  } catch (e) {
    toast.error('批量修改模型失败');
  }
};

const doAttachTags = async () => {
  try {
    const ids = Array.from(selectedIds.value);
    let totalAttached = 0;
    for (const tagId of (bulk.value.tagIds as any[])) {
      const res = await axios.post(`/api/v1/admin/tags/${tagId}/attach-images`, { image_ids: ids });
      totalAttached += res.data?.attached || 0;
    }
    toast.success(`已添加标签到 ${totalAttached} 张图片`);
    modal.value.attachTags = false;
    fetchImages();
  } catch (e) {
    toast.error('批量添加标签失败');
  }
};

const doDetachTags = async () => {
  try {
    const ids = Array.from(selectedIds.value);
    let totalDetached = 0;
    for (const tagId of (bulk.value.tagIds as any[])) {
      const res = await axios.post(`/api/v1/admin/tags/${tagId}/detach-images`, { image_ids: ids });
      totalDetached += res.data?.detached || 0;
    }
    toast.success(`已移除标签于 ${totalDetached} 张图片`);
    modal.value.detachTags = false;
    fetchImages();
  } catch (e) {
    toast.error('批量移除标签失败');
  }
};

const confirmBulkDelete = async () => {
  if (!confirm('确定要删除所选图片吗？如有子版本将跳过。')) return;
  try {
    // No dedicated bulk delete endpoint by ids; perform individually
    const ids = Array.from(selectedIds.value);
    for (const id of ids) {
      try { await axios.delete(`/api/v1/images/${id}`); } catch {}
    }
    toast.success('删除完成');
    fetchImages();
    selectedIds.value = new Set();
  } catch (e) {
    toast.error('批量删除失败');
  }
};

watch([search, () => filters.value.categoryId, () => filters.value.modelId, () => (filters.value.tagIds as any[]).join(',')], () => {
  page.value = 1;
  fetchImages();
});

onMounted(() => {
  fetchFilters();
  fetchImages();
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


