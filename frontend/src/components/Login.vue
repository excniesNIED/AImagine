<template>
  <div class="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-md">
      <!-- Login Card -->
      <Card class="shadow-lg">
        <CardHeader class="space-y-1 pb-6">
          <CardTitle class="text-2xl font-bold text-center">
            登录
          </CardTitle>
          <p class="text-center text-muted-foreground">
            输入您的账号信息
          </p>
        </CardHeader>

        <CardContent class="space-y-6">
          <form class="space-y-4" @submit.prevent="handleLogin">
            <div class="space-y-2">
              <Label for="username">用户名</Label>
              <Input
                id="username"
                v-model="formData.username"
                type="text"
                required
                placeholder="请输入用户名"
                autocomplete="username"
              />
            </div>

            <div class="space-y-2">
              <Label for="password">密码</Label>
              <Input
                id="password"
                v-model="formData.password"
                type="password"
                required
                placeholder="请输入密码"
                autocomplete="current-password"
              />
            </div>

            <Button
              type="submit"
              class="w-full"
              :disabled="isSubmitting"
            >
              <span v-if="isSubmitting" class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></span>
              {{ isSubmitting ? '登录中...' : '登录' }}
            </Button>
          </form>

          <!-- Alternative Actions -->
          <div class="text-center space-y-2">
            <div class="text-sm text-muted-foreground">
              还没有账号？
              <button
                @click="navigateToRegister"
                class="font-medium text-primary hover:underline transition-colors"
              >
                立即注册
              </button>
            </div>
            <button
              @click="navigateToHome"
              class="text-sm text-muted-foreground hover:text-primary hover:underline transition-colors"
            >
              ← 返回首页
            </button>
          </div>
        </CardContent>
      </Card>
    </div>

    <ToastContainer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import Card from './ui/Card.vue';
import CardHeader from './ui/CardHeader.vue';
import CardTitle from './ui/CardTitle.vue';
import CardContent from './ui/CardContent.vue';
import Label from './ui/Label.vue';
import Input from './ui/Input.vue';
import Button from './ui/Button.vue';
import ToastContainer from './ToastContainer.vue';
import { useToast } from '../composables/useToast';

const authStore = useAuthStore();
const { showToast } = useToast();

// If already logged in, redirect to home
onMounted(() => {
  if (authStore.isAuthenticated && authStore.user) {
    window.location.href = '/';
  }
});

const formData = ref({
  username: '',
  password: ''
});

const isSubmitting = ref(false);

const handleLogin = async () => {
  isSubmitting.value = true;

  try {
    const success = await authStore.login(formData.value);

    if (success) {
      showToast('登录成功！', 'success');
      // Give a small delay to ensure token is saved and toast is shown
      setTimeout(() => {
        window.location.href = '/';
      }, 500);
    } else {
      showToast('用户名或密码错误', 'error');
    }
  } catch (error: any) {
    showToast(error.response?.data?.detail || '登录失败', 'error');
  } finally {
    isSubmitting.value = false;
  }
};

const navigateToRegister = () => {
  window.location.href = '/register';
};

const navigateToHome = () => {
  window.location.href = '/';
};
</script>