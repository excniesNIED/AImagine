<template>
  <div v-if="open" class="fixed inset-0 z-50 bg-black/80" @click="open = false">
    <div class="fixed inset-0 z-50 flex" :class="positionClass">
      <div class="relative flex w-full max-w-sm flex-col bg-background p-6 shadow-lg">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  open: boolean
  side?: 'left' | 'right' | 'top' | 'bottom'
}

const props = withDefaults(defineProps<Props>(), {
  side: 'right'
})

const emit = defineEmits<{
  'update:open': [value: boolean]
}>()

const positionClass = computed(() => {
  switch (props.side) {
    case 'left':
      return 'justify-start'
    case 'right':
      return 'justify-end'
    case 'top':
      return 'flex-col justify-start'
    case 'bottom':
      return 'flex-col justify-end'
    default:
      return 'justify-end'
  }
})

const open = computed({
  get: () => props.open,
  set: (value) => emit('update:open', value)
})
</script>