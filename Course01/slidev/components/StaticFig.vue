<!-- A printed figure, as is: the course logistics and the dataset slides. The
     images are imported, so the single-file build inlines them. -->
<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{ name: string }>()
const all = import.meta.glob('../img/*.webp', { eager: true, query: '?url', import: 'default' }) as Record<string, string>
const src = computed(() => all[`../img/${props.name}.webp`])
</script>

<template>
  <div class="static"><img :src="src" :alt="name" /></div>
</template>

<style scoped>
.static { display: flex; align-items: center; justify-content: center; min-height: 0; height: 100%; }
img { max-width: 100%; max-height: 100%; object-fit: contain; }
</style>
