<script setup lang="ts">
defineProps<{ modelValue: boolean; label: string; color?: string }>()
const emit = defineEmits<{ 'update:modelValue': [boolean] }>()
</script>

<template>
  <label class="toggle">
    <input
      type="checkbox"
      :checked="modelValue"
      :style="{ accentColor: color || '#1b1b1b' }"
      @change="emit('update:modelValue', ($event.target as HTMLInputElement).checked)"
    />
    <span v-html="label" />
  </label>
</template>

<style scoped>
.toggle { display: inline-flex; align-items: center; gap: 0.35rem; font-size: 0.8rem; color: #3a3a3a; cursor: pointer; }
input { cursor: pointer; }
</style>
