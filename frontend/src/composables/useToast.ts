import { ref } from 'vue';

interface Toast {
  id: number;
  message: string;
  type: 'success' | 'error' | 'info' | 'warning';
}

const toasts = ref<Toast[]>([]);
let toastId = 0;

export const useToast = () => {
  const toast = (message: string, type: Toast['type'] = 'info', duration = 3000) => {
    const id = ++toastId;
    toasts.value.push({ id, message, type });

    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id);
    }, duration);
  };

  const success = (message: string, duration?: number) => toast(message, 'success', duration);
  const error = (message: string, duration?: number) => toast(message, 'error', duration);
  const info = (message: string, duration?: number) => toast(message, 'info', duration);
  const warning = (message: string, duration?: number) => toast(message, 'warning', duration);

  const removeToast = (id: number) => {
    toasts.value = toasts.value.filter(t => t.id !== id);
  };

  return {
    toasts,
    toast,
    success,
    error,
    info,
    warning,
    showToast: toast,
    removeToast,
  };
};