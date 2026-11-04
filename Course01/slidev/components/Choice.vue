<!-- A row of mutually exclusive buttons: the kernel picker, OvA vs OvO, ... -->
<script setup lang="ts">
defineProps<{
  modelValue: string
  options: { value: string; label: string; color?: string }[]
  label?: string
}>()
const emit = defineEmits<{ 'update:modelValue': [string] }>()
</script>

<template>
  <div class="choice">
    <span v-if="label" class="choice-label">{{ label }}</span>
    <button
      v-for="o in options"
      :key="o.value"
      :class="{ on: o.value === modelValue }"
      :style="o.value === modelValue ? { background: o.color || '#1b1b1b', borderColor: o.color || '#1b1b1b' } : { color: o.color || '#3a3a3a' }"
      @click="emit('update:modelValue', o.value)"
    >
      <span v-html="o.label" />
    </button>
  </div>
</template>

<style scoped>
.choice { display: flex; align-items: center; gap: 0.3rem; font-size: 0.8rem; }
.choice-label { color: #4a4a4a; margin-right: 0.2rem; }
button {
  border: 1px solid #d8dadd;
  border-radius: 0.3rem;
  padding: 0.16rem 0.5rem;
  background: white;
  cursor: pointer;
  line-height: 1.2;
  transition: all 0.12s;
}
button.on { color: white; font-weight: 600; }
button:not(.on):hover { border-color: #9aa0a6; }
</style>
