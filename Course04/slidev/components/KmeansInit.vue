<!-- kmeans_init: the same data, the same K, a different starting draw. The
     seed slider walks through the starts; the inertia says how unlucky each
     one was, and k-means++ is there to compare against. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { treeData } from '../lib/data4'
import { kmeans, kmeansPlusPlus, lloyd, randomInit } from '../lib/cluster'
import { GREEN, RED, clusterColor } from '../lib/theme'

const seed = ref(13)
const K = ref(5)
const X = treeData(3, 260, 0)
const dom: [number, number, number, number] = [-4.4, 5.0, -3.4, 3.4]

const best = computed(() => kmeans(X, K.value, 0, 10))
const one = computed(() => lloyd(X, randomInit(X, K.value, seed.value)))
const plus = computed(() => lloyd(X, kmeansPlusPlus(X, K.value, seed.value)))
const gap = computed(() => ((one.value.inertia / best.value.inertia - 1) * 100))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        :X="X" :labels="best.labels" :domain="dom" :point-size="2.2"
        :crosses="best.mu.map((m, k) => ({ x: m[0], y: m[1], color: clusterColor(k), size: 6 }))"
        title="k-means++, best of 10 restarts" :title-color="GREEN"
      />
      <ClusterPlot
        :X="X" :labels="plus.labels" :domain="dom" :point-size="2.2"
        :crosses="plus.mu.map((m, k) => ({ x: m[0], y: m[1], color: clusterColor(k), size: 6 }))"
        title="k-means++, one restart" :title-color="GREEN"
      />
      <ClusterPlot
        :X="X" :labels="one.labels" :domain="dom" :point-size="2.2"
        :crosses="one.mu.map((m, k) => ({ x: m[0], y: m[1], color: clusterColor(k), size: 6 }))"
        :title="`K random rows as the start (draw ${seed})`" :title-color="RED"
      />
    </div>
    <div class="controls">
      <Knob v-model="seed" :min="0" :max="60" :step="1" label="starting draw" :digits="0" :color="RED" />
      <Knob v-model="K" :min="2" :max="8" :step="1" label="K" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'inertia, best of 10', value: best.inertia.toFixed(0), color: GREEN },
          { label: 'one k-means++ start', value: plus.inertia.toFixed(0) },
          { label: 'this random start', value: one.inertia.toFixed(0), color: gap > 1 ? RED : GREEN },
          { label: 'worse by', value: `${gap.toFixed(1)}%`, color: gap > 1 ? RED : GREEN },
        ]"
      />
      <span class="note">Lloyd's algorithm only ever finds a local minimum, so
        where the centres start decides which one.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; min-height: 0; }
.controls { display: flex; gap: 1.3rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 11rem; }
</style>
