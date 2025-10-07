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
  modelValue: string | number | null | undefined;
  options: OptionItem[];
  placeholder?: string;
  disabled?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:modelValue', v: string | number | null): void;
  (e: 'change', v: string | number | null): void;
}>();

const open = ref(false);
const container = ref<HTMLElement | null>(null);

const selectedLabel = computed(() => {
  const mv = props.modelValue;
  if (mv === null || mv === undefined || mv === '') return '';
  return props.options.find(o => String(o.value) === String(mv))?.label || '';
});

const toggle = () => {
  if (props.disabled) return;
  open.value = !open.value;
};

const select = (v: string | number) => {
  emit('update:modelValue', v);
  emit('change', v);
  open.value = false;
};

const isSelected = (v: string | number) => String(v) === String(props.modelValue ?? '');

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


