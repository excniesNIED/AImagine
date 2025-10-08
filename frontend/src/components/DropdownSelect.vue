<template>
  <div class="dropdown-container" ref="container">
    <button
      type="button"
      class="dropdown-button w-full"
      :aria-expanded="open ? 'true' : 'false'"
      @click="toggle"
    >
      <span class="truncate">{{ selectedLabel || placeholder }}</span>
      <svg class="w-4 h-4 ml-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div v-if="open" class="dropdown-menu">
      <div v-if="(multiple || clearable)" class="flex items-center justify-between px-3 py-2 border-b border-gray-200 dark:border-gray-700">
        <span class="text-sm text-gray-500">{{ multiple ? '多选' : '单选' }}</span>
        <button type="button" class="text-xs text-gray-600 dark:text-gray-300 hover:text-primary-600" @click="clearSelection" :disabled="!hasSelection">
          清空
        </button>
      </div>
      <button
        v-for="opt in options"
        :key="String(opt.value)"
        type="button"
        class="dropdown-item flex justify-between"
        @click="select(opt.value)"
      >
        <span class="truncate">{{ opt.label }}</span>
        <svg v-if="isSelected(opt.value)" class="w-4 h-4 text-primary-600 dark:text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';

interface OptionItem {
  value: string | number;
  label: string;
}

const props = defineProps<{
  modelValue: string | number | Array<string | number> | null | undefined;
  options: OptionItem[];
  placeholder?: string;
  disabled?: boolean;
  multiple?: boolean;
  clearable?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', v: string | number | Array<string | number> | null): void;
  (e: 'change', v: string | number | Array<string | number> | null): void;
}>();

const open = ref(false);
const container = ref<HTMLElement | null>(null);

const selectedLabel = computed(() => {
  const mv = props.modelValue as any;
  if (props.multiple) {
    const arr: Array<string | number> = Array.isArray(mv) ? mv : [];
    if (!arr.length) return '';
    const labels = arr
      .map(v => props.options.find(o => String(o.value) === String(v))?.label || String(v))
      .filter(Boolean);
    if (labels.length <= 2) return labels.join(', ');
    return `${labels.slice(0, 2).join(', ')} 等${labels.length}项`;
  } else {
    if (mv === null || mv === undefined || mv === '') return '';
    return props.options.find(o => String(o.value) === String(mv))?.label || '';
  }
});

const toggle = () => {
  if (props.disabled) return;
  open.value = !open.value;
};

const select = (v: string | number) => {
  if (props.multiple) {
    const current = Array.isArray(props.modelValue) ? [...(props.modelValue as Array<string | number>)] : [];
    const idx = current.findIndex(x => String(x) === String(v));
    if (idx >= 0) {
      current.splice(idx, 1);
    } else {
      current.push(v);
    }
    emit('update:modelValue', current);
    emit('change', current);
  } else {
    emit('update:modelValue', v);
    emit('change', v);
    open.value = false;
  }
};

const isSelected = (v: string | number) => {
  if (props.multiple) {
    const current = Array.isArray(props.modelValue) ? (props.modelValue as Array<string | number>) : [];
    return current.some(x => String(x) === String(v));
  }
  return String(v) === String((props.modelValue as any) ?? '');
};

const hasSelection = computed(() => {
  if (props.multiple) return Array.isArray(props.modelValue) && (props.modelValue as Array<any>).length > 0;
  return !!props.modelValue;
});

const clearSelection = () => {
  if (!hasSelection.value) return;
  if (props.multiple) {
    emit('update:modelValue', []);
    emit('change', []);
  } else {
    emit('update:modelValue', '');
    emit('change', '');
  }
};

const onClickOutside = (e: MouseEvent) => {
  if (!open.value) return;
  if (container.value && !container.value.contains(e.target as Node)) {
    open.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', onClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener('click', onClickOutside);
});
</script>

<style scoped>
/* Ensure the dropdown menu aligns to the trigger width */
.dropdown-menu {
  width: 100%;
}
</style>


