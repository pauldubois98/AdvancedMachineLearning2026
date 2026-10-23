<!-- Horizontal bars with a word on each: the heaviest words of a post or a
     topic. Plain HTML, so the words stay crisp at any size. -->
<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ items: { label: string; value: number }[]; color: string }>()
const vmax = computed(() => Math.max(...props.items.map((i) => i.value), 1e-12))
</script>

<template>
  <div class="hbars">
    <div v-for="it in items" :key="it.label" class="row">
      <span class="lab">{{ it.label }}</span>
      <span class="bar" :style="{ width: `${(100 * it.value) / vmax}%`, background: color }" />
    </div>
  </div>
</template>

<style scoped>
.hbars { display: flex; flex-direction: column; justify-content: center; gap: 0.3rem; height: 100%; }
.row { display: grid; grid-template-columns: 6.5rem 1fr; gap: 0.5rem; align-items: center; font-size: 0.8rem; }
.lab { text-align: right; }
.bar { display: block; height: 0.8rem; border-radius: 1px; transition: width 0.2s; }
</style>
