<template>
  <div class="relative">
    <slot name="trigger" :open="open" :toggle="toggle" />

    <div
      v-if="open"
      class="absolute top-full z-50 min-w-8 overflow-hidden rounded-md border bg-popover p-1 text-popover-foreground shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2"
      :class="[align === 'end' ? 'right-0' : 'left-0']"
    >
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  align?: 'start' | 'end'
}

const props = withDefaults(defineProps<Props>(), {
  align: 'start'
})

const open = ref(false)

const toggle = () => {
  open.value = !open.value
}

defineExpose({
  open,
  toggle
})
</script>