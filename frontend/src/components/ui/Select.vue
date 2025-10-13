<template>
  <div class="relative">
    <button
      type="button"
      :class="cn(
        'flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
        props.class
      )"
      @click="toggleOpen"
    >
      <span class="truncate">{{ selectedLabel || placeholder }}</span>
      <ChevronDown :class="cn('h-4 w-4 opacity-50 transition-transform', open && 'rotate-180')" />
    </button>

    <div
      v-if="open"
      class="absolute top-full z-50 mt-1 max-h-60 w-full overflow-auto rounded-md border bg-popover text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2"
    >
      <div v-if="(multiple || clearable)" class="flex items-center justify-between px-3 py-2 border-b border-border">
        <span class="text-sm text-muted-foreground">{{ multiple ? '多选' : '单选' }}</span>
        <Button
          type="button"
          variant="ghost"
          size="sm"
          @click="clearSelection"
          :disabled="!hasSelection"
        >
          清空
        </Button>
      </div>

      <div class="p-1">
        <button
          v-for="option in options"
          :key="String(option.value)"
          type="button"
          :class="cn(
            'relative flex w-full cursor-pointer select-none items-center rounded-sm py-1.5 pl-8 pr-2 text-sm outline-none hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground',
            isSelected(option.value) && 'bg-accent text-accent-foreground'
          )"
          @click="select(option.value)"
        >
          <span class="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
            <Check v-if="isSelected(option.value)" class="h-4 w-4" />
          </span>
          <span class="truncate">{{ option.label }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { cn } from '@/lib/utils'
import { ChevronDown, Check } from 'lucide-vue-next'
import Button from './Button.vue'

interface Option {
  label: string
  value: string | number
}

interface Props {
  modelValue?: string | number | Array<string | number>
  options: Option[]
  placeholder?: string
  multiple?: boolean
  clearable?: boolean
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '请选择...',
  multiple: false,
  clearable: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number | Array<string | number>]
  'change': [value: string | number | Array<string | number>]
}>()

const open = ref(false)

const selectedLabel = computed(() => {
  if (props.multiple) {
    const values = Array.isArray(props.modelValue) ? props.modelValue : []
    if (values.length === 0) return ''
    if (values.length === 1) {
      const option = props.options.find(opt => opt.value === values[0])
      return option?.label || ''
    }
    return `已选择 ${values.length} 项`
  } else {
    const option = props.options.find(opt => opt.value === props.modelValue)
    return option?.label || ''
  }
})

const hasSelection = computed(() => {
  if (props.multiple) {
    const values = Array.isArray(props.modelValue) ? props.modelValue : []
    return values.length > 0
  }
  return props.modelValue !== undefined && props.modelValue !== ''
})

const isSelected = (value: string | number) => {
  if (props.multiple) {
    const values = Array.isArray(props.modelValue) ? props.modelValue : []
    return values.includes(value)
  }
  return props.modelValue === value
}

const toggleOpen = () => {
  open.value = !open.value
}

const select = (value: string | number) => {
  if (props.multiple) {
    const values = Array.isArray(props.modelValue) ? [...props.modelValue] : []
    const index = values.indexOf(value)
    if (index > -1) {
      values.splice(index, 1)
    } else {
      values.push(value)
    }
    emit('update:modelValue', values)
    emit('change', values)
  } else {
    emit('update:modelValue', value)
    emit('change', value)
    open.value = false
  }
}

const clearSelection = () => {
  if (props.multiple) {
    emit('update:modelValue', [])
    emit('change', [])
  } else {
    emit('update:modelValue', '')
    emit('change', '')
  }
}

const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Element
  if (!target.closest('.relative')) {
    open.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>