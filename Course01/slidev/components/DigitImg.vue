<!-- one 8 x 8 digit, grey levels 0 (white) to 16 (black), as matplotlib's gray_r -->
<script setup lang="ts">
defineProps<{ px: number[] }>()
const shade = (v: number) => { const g = Math.round(255 * (1 - Math.min(1, Math.max(0, v / 16)))); return `rgb(${g},${g},${g})` }
</script>

<template>
  <svg viewBox="0 0 8 8" class="digit" shape-rendering="crispEdges">
    <rect v-for="(v, i) in px" :key="i" :x="i % 8" :y="Math.floor(i / 8)" width="1.02" height="1.02" :style="{ fill: shade(v) }" />
  </svg>
</template>

<style scoped>
.digit { width: 100%; aspect-ratio: 1; display: block; outline: 1px solid #cccfd2; }
</style>
