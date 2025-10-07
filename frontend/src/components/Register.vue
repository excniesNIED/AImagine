<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-gray-100">
          注册新账号
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          已有账号？
          <a href="/login" class="font-medium text-primary-600 hover:text-primary-500">
            立即登录
          </a>
        </p>
      </div>
      
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="space-y-4">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              用户名
            </label>
            <input
              id="username"
              v-model="formData.username"
              type="text"
              required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="输入用户名"
            />
          </div>
          
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              邮箱
            </label>
            <input
              id="email"
              v-model="formData.email"
              type="email"
              required
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="输入邮箱地址"
            />
          </div>
          
          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              密码
            </label>
            <input
              id="password"
              v-model="formData.password"
              type="password"
              required
              minlength="6"
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="输入密码（至少6位）"
            />
          </div>
          
          <div>
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              确认密码
            </label>
            <input
              id="confirmPassword"
              v-model="formData.confirmPassword"
              type="password"
              required
              minlength="6"
              class="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-gray-100 bg-white dark:bg-gray-800 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500"
              placeholder="再次输入密码"
            />
          </div>
        </div>
        
        <div>
          <button
            type="submit"
            :disabled="isSubmitting || !isFormValid"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isSubmitting" class="inline-block animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></span>
            {{ isSubmitting ? '注册中...' : '注册' }}
          </button>
        </div>
        
        <div class="text-center">
          <a href="/" class="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-600 dark:hover:text-primary-400">
            返回首页
          </a>
        </div>
      </form>
    </div>
    
    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import ToastContainer from './ToastContainer.vue';
import { useToast } from '../composables/useToast';

const authStore = useAuthStore();
const { showToast } = useToast();

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
});

const isSubmitting = ref(false);

const isFormValid = computed(() => {
  return (
    formData.value.username.length > 0 &&
    formData.value.email.length > 0 &&
    formData.value.password.length >= 6 &&
    formData.value.password === formData.value.confirmPassword
  );
});

const handleRegister = async () => {
  if (!isFormValid.value) {
    if (formData.value.password !== formData.value.confirmPassword) {
      showToast('两次输入的密码不一致', 'error');
    }
    return;
  }
  
  isSubmitting.value = true;
  
  try {
    const success = await authStore.register({
      username: formData.value.username,
      email: formData.value.email,
      password: formData.value.password
    });
    
    if (success) {
      showToast('注册成功！请登录', 'success');
      window.location.href = '/login';
    } else {
      showToast('注册失败', 'error');
    }
  } catch (error: any) {
    showToast(error.response?.data?.detail || '注册失败', 'error');
  } finally {
    isSubmitting.value = false;
  }
};
</script>