<template>
  <div class="space-y-6">
    <!-- Alist Settings -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-6">Alist (Openlist) 配置</h2>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-2">Alist URL</label>
          <input
            v-model="alistSettings.url"
            type="url"
            placeholder="http://localhost:5244"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500"
          />
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">API Token</label>
          <input
            v-model="alistSettings.token"
            type="password"
            placeholder="Alist API Token"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500"
          />
          <p class="text-sm text-gray-500 mt-1">优先使用 Token，如未配置则使用用户名密码</p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-2">用户名</label>
            <input
              v-model="alistSettings.username"
              type="text"
              placeholder="admin"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <div>
            <label class="block text-sm font-medium mb-2">密码</label>
            <input
              v-model="alistSettings.password"
              type="password"
              placeholder="••••••••"
              class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-2">默认上传路径</label>
          <input
            v-model="alistSettings.uploadPath"
            type="text"
            placeholder="/gallery"
            class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 focus:ring-2 focus:ring-primary-500"
          />
          <p class="text-sm text-gray-500 mt-1">文件将上传到此路径下的用户ID子目录中</p>
        </div>
      </div>

      <div class="mt-6 flex gap-4">
        <button
          @click="testConnection"
          :disabled="testing"
          class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ testing ? '测试中...' : '测试连接' }}
        </button>
        <button
          @click="saveSettings"
          class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          保存设置
        </button>
      </div>

      <div v-if="connectionStatus" class="mt-4">
        <div
          :class="[
            'p-4 rounded-lg',
            connectionStatus.success
              ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
              : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
          ]"
        >
          {{ connectionStatus.message }}
        </div>
      </div>
    </div>

    <!-- System Info -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
      <h2 class="text-xl font-semibold mb-4">系统信息</h2>

      <div class="space-y-3">
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">项目名称</span>
          <span class="font-medium">AI Gallery</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">版本</span>
          <span class="font-medium">1.0.0</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">后端 API</span>
          <span class="font-medium">/api/v1</span>
        </div>
        <div class="flex justify-between">
          <span class="text-gray-600 dark:text-gray-400">数据库</span>
          <span class="font-medium">SQLite</span>
        </div>
      </div>
    </div>

    <!-- Danger Zone -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-6 border-2 border-red-200 dark:border-red-800">
      <h2 class="text-xl font-semibold mb-4 text-red-600 dark:text-red-400">危险区域</h2>
      <p class="text-gray-600 dark:text-gray-400 mb-4">
        以下操作不可逆，请谨慎操作
      </p>
      <button
        @click="confirmReset = true"
        class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
      >
        重置系统
      </button>
    </div>

    <!-- Reset Confirmation Modal -->
    <div v-if="confirmReset" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <h3 class="text-xl font-semibold mb-4 text-red-600 dark:text-red-400">确认重置系统</h3>
        <p class="text-gray-600 dark:text-gray-400 mb-4">
          此操作将删除所有数据（用户、图片、分类、标签、模型），且无法恢复。
        </p>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          请输入 <code class="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">RESET</code> 确认：
        </p>
        <input
          v-model="resetConfirmation"
          type="text"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 mb-4"
          placeholder="输入 RESET"
        />
        <div class="flex justify-end gap-2">
          <button @click="confirmReset = false" class="btn-secondary">取消</button>
          <button
            @click="resetSystem"
            :disabled="resetConfirmation !== 'RESET'"
            class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            确认重置
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from '../../utils/axios';
import { useToast } from '../../composables/useToast';

const toast = useToast();

interface AlistSettings {
  url: string;
  token: string;
  username: string;
  password: string;
  uploadPath: string;
}

const alistSettings = ref<AlistSettings>({
  url: '',
  token: '',
  username: '',
  password: '',
  uploadPath: '/gallery'
});

const testing = ref(false);
const connectionStatus = ref<{ success: boolean; message: string } | null>(null);
const confirmReset = ref(false);
const resetConfirmation = ref('');

const fetchSettings = async () => {
  try {
    const response = await axios.get('/api/v1/admin/settings');
    alistSettings.value = {
      url: response.data.alist.url || '',
      token: '',
      username: response.data.alist.username || '',
      password: '',
      uploadPath: response.data.alist.upload_path || '/gallery'
    };
  } catch (error) {
    console.error('Failed to fetch settings:', error);
  }
};

const testConnection = async () => {
  testing.value = true;
  connectionStatus.value = null;

  try {
    const response = await axios.post('/api/v1/admin/settings/test-alist');
    connectionStatus.value = {
      success: response.data.success,
      message: response.data.message
    };
  } catch (error) {
    connectionStatus.value = {
      success: false,
      message: '连接测试失败'
    };
  } finally {
    testing.value = false;
  }
};

const saveSettings = async () => {
  try {
    // Only send non-empty values to avoid wiping existing credentials
    const payload: Record<string, string> = {};
    if (alistSettings.value.url && alistSettings.value.url.trim()) payload.url = alistSettings.value.url.trim();
    if (alistSettings.value.token && alistSettings.value.token.trim()) payload.token = alistSettings.value.token.trim();
    if (alistSettings.value.username && alistSettings.value.username.trim()) payload.username = alistSettings.value.username.trim();
    if (alistSettings.value.password && alistSettings.value.password) payload.password = alistSettings.value.password;
    if (alistSettings.value.uploadPath && alistSettings.value.uploadPath.trim()) payload.upload_path = alistSettings.value.uploadPath.trim();
    await axios.post('/api/v1/admin/settings/alist', payload);
    toast.success('设置已保存');
    // Clear sensitive fields in UI
    alistSettings.value.token = '';
    alistSettings.value.password = '';
    // Refresh display values
    await fetchSettings();
  } catch (error) {
    toast.error('保存设置失败');
    console.error('Failed to save settings:', error);
  }
};

const resetSystem = async () => {
  if (resetConfirmation.value !== 'RESET') return;

  try {
    // Note: This would require a special admin endpoint for system reset
    // For security, this should require additional confirmation
    toast.error('系统重置功能暂未实现');
    confirmReset.value = false;
    resetConfirmation.value = '';
  } catch (error) {
    toast.error('重置系统失败');
    console.error('Failed to reset system:', error);
  }
};

onMounted(() => {
  fetchSettings();
});
</script>

<style scoped>
.btn-secondary {
  @apply px-4 py-2 bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors;
}
</style>