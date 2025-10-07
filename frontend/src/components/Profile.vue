<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <AppHeader />
    
    <main class="max-w-4xl mx-auto px-4 py-8">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <h1 class="text-3xl font-bold mb-8 text-gray-900 dark:text-white">个人资料</h1>
        
        <div v-if="loading" class="flex justify-center py-12">
          <LoadingAnimation />
        </div>
        
        <div v-else class="space-y-6">
          <!-- User Info Display -->
          <div v-if="!editing" class="space-y-4">
            <div class="border-b border-gray-200 dark:border-gray-700 pb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">用户名</label>
              <p class="text-lg text-gray-900 dark:text-white">{{ user?.username }}</p>
            </div>
            
            <div class="border-b border-gray-200 dark:border-gray-700 pb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">邮箱</label>
              <p class="text-lg text-gray-900 dark:text-white">{{ user?.email }}</p>
            </div>
            
            <div class="border-b border-gray-200 dark:border-gray-700 pb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">角色</label>
              <span 
                class="inline-block px-3 py-1 text-sm rounded-full"
                :class="user?.role === 'admin' 
                  ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' 
                  : 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200'"
              >
                {{ user?.role === 'admin' ? '管理员' : '普通用户' }}
              </span>
            </div>
            
            <div class="border-b border-gray-200 dark:border-gray-700 pb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">账号状态</label>
              <span 
                class="inline-block px-3 py-1 text-sm rounded-full"
                :class="user?.is_active 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'"
              >
                {{ user?.is_active ? '正常' : '已停用' }}
              </span>
            </div>
            
            <div class="border-b border-gray-200 dark:border-gray-700 pb-4">
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">注册时间</label>
              <p class="text-lg text-gray-900 dark:text-white">{{ formatDate(user?.created_at) }}</p>
            </div>
            
            <div class="flex gap-4 mt-8">
              <button
                @click="editing = true"
                class="btn-primary"
              >
                编辑资料
              </button>
              <button
                @click="showPasswordChange = true"
                class="btn-secondary"
              >
                修改密码
              </button>
            </div>
          </div>
          
          <!-- Edit Form -->
          <form v-else @submit.prevent="updateProfile" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">用户名</label>
              <input
                v-model="editForm.username"
                type="text"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">邮箱</label>
              <input
                v-model="editForm.email"
                type="email"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                required
              />
            </div>
            
            <div class="flex gap-4 mt-8">
              <button
                type="submit"
                class="btn-primary"
                :disabled="updating"
              >
                {{ updating ? '保存中...' : '保存' }}
              </button>
              <button
                type="button"
                @click="cancelEdit"
                class="btn-secondary"
                :disabled="updating"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
      
      <!-- Change Password Modal -->
      <div v-if="showPasswordChange" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" @click.self="showPasswordChange = false">
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-md w-full mx-4">
          <h2 class="text-2xl font-bold mb-6 text-gray-900 dark:text-white">修改密码</h2>
          
          <form @submit.prevent="changePassword" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">新密码</label>
              <input
                v-model="passwordForm.newPassword"
                type="password"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                required
                minlength="6"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">确认新密码</label>
              <input
                v-model="passwordForm.confirmPassword"
                type="password"
                class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 dark:bg-gray-700 dark:text-white"
                required
                minlength="6"
              />
            </div>
            
            <div class="flex gap-4 mt-8">
              <button
                type="submit"
                class="btn-primary"
                :disabled="changingPassword"
              >
                {{ changingPassword ? '修改中...' : '确认修改' }}
              </button>
              <button
                type="button"
                @click="closePasswordModal"
                class="btn-secondary"
                :disabled="changingPassword"
              >
                取消
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
    
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import axios from '../utils/axios';
import AppHeader from './AppHeader.vue';
import ToastContainer from './ToastContainer.vue';
import LoadingAnimation from './LoadingAnimation.vue';
import { useAuthStore } from '../stores/auth';
import { useToast } from '../composables/useToast';

const authStore = useAuthStore();
const toast = useToast();

const loading = ref(true);
const editing = ref(false);
const updating = ref(false);
const showPasswordChange = ref(false);
const changingPassword = ref(false);

const user = computed(() => authStore.user);

const editForm = ref({
  username: '',
  email: ''
});

const passwordForm = ref({
  newPassword: '',
  confirmPassword: ''
});

const fetchUserProfile = async () => {
  try {
    loading.value = true;
    const response = await axios.get('/api/v1/users/me');
    // User is already in the auth store, just ensure it's up to date
    if (response.data) {
      authStore.user = response.data;
    }
  } catch (error) {
    console.error('Failed to fetch user profile:', error);
    toast.error('获取用户信息失败');
  } finally {
    loading.value = false;
  }
};

const updateProfile = async () => {
  try {
    updating.value = true;
    await axios.put('/api/v1/users/me', editForm.value);
    await authStore.fetchProfile();
    toast.success('资料更新成功');
    editing.value = false;
  } catch (error: any) {
    console.error('Failed to update profile:', error);
    toast.error(error.response?.data?.detail || '更新资料失败');
  } finally {
    updating.value = false;
  }
};

const changePassword = async () => {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    toast.error('两次输入的密码不一致');
    return;
  }
  
  try {
    changingPassword.value = true;
    await axios.put('/api/v1/users/me/password', {
      password: passwordForm.value.newPassword
    });
    toast.success('密码修改成功');
    closePasswordModal();
  } catch (error: any) {
    console.error('Failed to change password:', error);
    toast.error(error.response?.data?.detail || '修改密码失败');
  } finally {
    changingPassword.value = false;
  }
};

const cancelEdit = () => {
  editing.value = false;
  if (user.value) {
    editForm.value = {
      username: user.value.username,
      email: user.value.email
    };
  }
};

const closePasswordModal = () => {
  showPasswordChange.value = false;
  passwordForm.value = {
    newPassword: '',
    confirmPassword: ''
  };
};

const formatDate = (dateString?: string) => {
  if (!dateString) return '';
  return new Date(dateString).toLocaleString('zh-CN');
};

onMounted(async () => {
  await fetchUserProfile();
  if (user.value) {
    editForm.value = {
      username: user.value.username,
      email: user.value.email
    };
  }
});
</script>

