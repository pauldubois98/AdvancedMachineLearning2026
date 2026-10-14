<!-- linkage_compare: the same cloud under four linkages. The noise slider adds
     the stray points single linkage chains through. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { treeData } from '../lib/data4'
import { Method, fclusterMaxclust, linkage } from '../lib/hier'
import { BLUE, GREEN, PURPLE, RED } from '../lib/theme'

const noise = ref(25)
const k = ref(3)
const X = computed(() => treeData(3, 260, Math.round(noise.value)))
const methods: { m: Method; name: string; formula: string; color: string; cap: string }[] = [
  { m: 'single', name: 'single', formula: 'minₓ,ᵧ D(x, y)', color: BLUE, cap: '"one bridge of points is enough"' },
  { m: 'complete', name: 'complete', formula: 'maxₓ,ᵧ D(x, y)', color: RED, cap: '"far ends must be close too"' },
  { m: 'average', name: 'average', formula: 'meanₓ,ᵧ D(x, y)', color: GREEN, cap: '"between single and complete"' },
  { m: 'ward', name: 'ward', formula: 'ΔJ<sub>w</sub> of the merge', color: PURPLE, cap: '"the smallest jump in inertia"' },
]
const runs = computed(() =>
  methods.map((spec) => {
    const labels = fclusterMaxclust(linkage(X.value, spec.m), k.value)
    const sizes = [...new Set(labels)].map((l) => labels.filter((v) => v === l).length).sort((a, b) => b - a)
    return { ...spec, labels, sizes }
  }),
)
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div v-for="r in runs" :key="r.m" class="col">
        <ClusterPlot
          :X="X" :labels="r.labels" :point-size="2"
          :title="`${r.name}<br><span style='font-weight:400;font-size:0.76rem'>${r.formula}</span>`"
          :title-color="r.color"
        />
        <div class="note">{{ r.cap }}<br />sizes: {{ r.sizes.join(' / ') }}</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="noise" :min="0" :max="80" :step="1" label="stray points added" :digits="0" :color="RED" />
      <Knob v-model="k" :min="2" :max="6" :step="1" label="clusters kept" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'biggest cluster, single', value: `${runs[0].sizes[0]} of ${X.length}`, color: BLUE },
          { label: 'biggest cluster, Ward', value: `${runs[3].sizes[0]} of ${X.length}`, color: PURPLE },
        ]"
      />
      <span class="note">with enough strays single linkage returns one huge
        cluster and a few singletons: the chaining effect</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.8rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.col .note { text-align: center; line-height: 1.4; }
.controls { display: flex; gap: 1.3rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
</style>
