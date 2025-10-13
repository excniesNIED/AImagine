<template>
  <div class="min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8">
    <div class="w-full max-w-md">
      <!-- Register Card -->
      <Card class="shadow-lg">
        <CardHeader class="space-y-1 pb-6">
          <CardTitle class="text-2xl font-bold text-center">
            注册
          </CardTitle>
          <p class="text-center text-muted-foreground">
            创建新账号
          </p>
        </CardHeader>

        <CardContent class="space-y-6">
          <form class="space-y-4" @submit.prevent="handleRegister">
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
              <Label for="email">邮箱地址</Label>
              <Input
                id="email"
                v-model="formData.email"
                type="email"
                required
                placeholder="请输入邮箱地址"
                autocomplete="email"
              />
            </div>

            <div class="space-y-2">
              <Label for="password">密码</Label>
              <Input
                id="password"
                v-model="formData.password"
                type="password"
                required
                minlength="6"
                placeholder="请输入密码（至少6位）"
                autocomplete="new-password"
              />
              <p class="text-xs text-muted-foreground">密码需要至少6个字符</p>
            </div>

            <div class="space-y-2">
              <Label for="confirmPassword">确认密码</Label>
              <Input
                id="confirmPassword"
                v-model="formData.confirmPassword"
                type="password"
                required
                minlength="6"
                placeholder="请再次输入密码"
                autocomplete="new-password"
                :class="{ 'border-destructive': formData.confirmPassword && formData.password !== formData.confirmPassword }"
              />
              <p v-if="formData.confirmPassword && formData.password !== formData.confirmPassword" class="text-xs text-destructive">
                两次输入的密码不一致
              </p>
            </div>

            <Button
              type="submit"
              class="w-full"
              :disabled="isSubmitting || !isFormValid"
            >
              <span v-if="isSubmitting" class="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2"></span>
              {{ isSubmitting ? '注册中...' : '注册' }}
            </Button>
          </form>

          <!-- Alternative Actions -->
          <div class="text-center space-y-2">
            <div class="text-sm text-muted-foreground">
              已有账号？
              <button
                @click="navigateToLogin"
                class="font-medium text-primary hover:underline transition-colors"
              >
                立即登录
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
import { ref, computed } from 'vue';
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

const navigateToLogin = () => {
  window.location.href = '/login';
};

const navigateToHome = () => {
  window.location.href = '/';
};
</script>