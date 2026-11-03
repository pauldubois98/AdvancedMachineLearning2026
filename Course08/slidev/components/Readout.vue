<!-- The grey caption line the printed figures carry under each panel. -->
<script setup lang="ts">
defineProps<{ items: { label: string; value: string; color?: string }[] }>()
</script>

<template>
  <div class="readout">
    <span v-for="(it, i) in items" :key="i" class="item">
      <span class="lab" v-html="it.label" />
      <span class="val" :style="{ color: it.color || '#1b1b1b' }" v-html="it.value" />
    </span>
  </div>
</template>

<style scoped>
.readout { display: flex; flex-wrap: wrap; gap: 0 1.1rem; font-size: 0.8rem; align-items: baseline; }
.item { display: inline-flex; gap: 0.3rem; align-items: baseline; }
.lab { color: #9aa0a6; }
.val { font-weight: 600; font-variant-numeric: tabular-nums; }
</style>
