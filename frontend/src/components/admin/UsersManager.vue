<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
    <div class="p-6 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-semibold">用户管理</h2>
    </div>
    <div class="p-6">
      <div v-if="loading" class="text-center py-8">
        <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="border-b border-gray-200 dark:border-gray-700">
              <th class="text-left py-3 px-4">用户ID</th>
              <th class="text-left py-3 px-4">用户名</th>
              <th class="text-left py-3 px-4">角色</th>
              <th class="text-left py-3 px-4">状态</th>
              <th class="text-left py-3 px-4">注册时间</th>
              <th class="text-left py-3 px-4">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in users"
              :key="user.id"
              class="border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              <td class="py-3 px-4">{{ user.id }}</td>
              <td class="py-3 px-4 font-medium">{{ user.username }}</td>
              <td class="py-3 px-4">
                <select
                  :value="user.role"
                  @change="updateUserRole(user.id, $event.target.value)"
                  class="px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm bg-white dark:bg-gray-700"
                  :disabled="user.id === currentUser?.id"
                >
                  <option value="user">普通用户</option>
                  <option value="admin">管理员</option>
                </select>
              </td>
              <td class="py-3 px-4">
                <button
                  @click="toggleUserStatus(user)"
                  :class="[
                    'px-2 py-1 rounded text-xs font-medium transition-colors',
                    user.is_active
                      ? 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300 hover:bg-green-200 dark:hover:bg-green-800'
                      : 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-800'
                  ]"
                  :disabled="user.id === currentUser?.id"
                >
                  {{ user.is_active ? '激活' : '禁用' }}
                </button>
              </td>
              <td class="py-3 px-4 text-gray-500">{{ formatDate(user.created_at) }}</td>
              <td class="py-3 px-4">
                <div class="flex gap-2">
                  <button
                    @click="viewUserImages(user.id)"
                    class="px-2 py-1 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                  >
                    查看作品
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from '../../utils/axios';
import { useToast } from '../../composables/useToast';
import { useAuthStore } from '../../stores/auth';

const toast = useToast();
const authStore = useAuthStore();

interface User {
  id: number;
  username: string;
  role: 'admin' | 'user';
  is_active: boolean;
  created_at: string;
}

const users = ref<User[]>([]);
const loading = ref(true);

const currentUser = authStore.user;

const fetchUsers = async () => {
  try {
    loading.value = true;
    const response = await axios.get('/api/v1/admin/users');
    users.value = response.data.users;
  } catch (error) {
    toast.error('获取用户列表失败');
    console.error('Failed to fetch users:', error);
  } finally {
    loading.value = false;
  }
};

const updateUserRole = async (userId: number, newRole: string) => {
  try {
    await axios.put(`/api/v1/admin/users/${userId}/role`, { role: newRole });
    toast.success('用户角色更新成功');

    // Update local user in auth store if it's the current user
    if (authStore.user && authStore.user.id === userId) {
      authStore.user.role = newRole;
    }

    fetchUsers();
  } catch (error) {
    toast.error('更新用户角色失败');
    console.error('Failed to update user role:', error);
  }
};

const toggleUserStatus = async (user: User) => {
  if (user.id === currentUser?.id) {
    toast.error('不能修改自己的状态');
    return;
  }

  const action = user.is_active ? '禁用' : '激活';
  if (!confirm(`确定要${action}用户 ${user.username} 吗？`)) return;

  try {
    await axios.put(`/api/v1/admin/users/${user.id}/status`, {
      is_active: !user.is_active
    });
    toast.success(`用户${action}成功`);
    fetchUsers();
  } catch (error) {
    toast.error(`${action}用户失败`);
    console.error('Failed to update user status:', error);
  }
};

const viewUserImages = (userId: number) => {
  const params = new URLSearchParams({ user_id: userId.toString() });
  window.location.href = `/?${params.toString()}`;
};

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN');
};

onMounted(() => {
  fetchUsers();
});
</script>