<!-- linkage_dendrograms: the shape of the tree is the signature of the
     linkage. Same points, same order, four very different trees. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { treeData } from '../lib/data4'
import { Method, linkage } from '../lib/hier'
import { BLUE, GREEN, PURPLE, RED } from '../lib/theme'

const noise = ref(25)
const n = ref(120)
const X = computed(() => treeData(3, Math.round(n.value), Math.round(noise.value)))
const specs: { m: Method; title: string; sub: string; color: string; cap: string }[] = [
  { m: 'single', title: 'single', sub: 'nearest pair of points', color: BLUE, cap: 'everything joins one growing chain' },
  { m: 'complete', title: 'complete', sub: 'farthest pair of points', color: RED, cap: 'splits large groups' },
  { m: 'average', title: 'average', sub: 'mean over all pairs', color: GREEN, cap: 'balanced' },
  { m: 'ward', title: 'ward', sub: 'inertia added by the merge', color: PURPLE, cap: 'also balanced, and more so' },
]
const trees = computed(() =>
  specs.map((s) => {
    const Z = linkage(X.value, s.m)
    // Chaining shows up at the top of the tree: a chain keeps adding one more
    // point to the same growing cluster, so count how many of the last merges
    // join a single point rather than two groups.
    const n0 = Z.length + 1
    const size = new Array(2 * n0 - 1).fill(1)
    Z.forEach((m, r) => { size[n0 + r] = m.size })
    const late = Z.slice(Math.floor(0.75 * Z.length))
    const singles = late.filter((m) => Math.min(size[m.a], size[m.b]) === 1).length
    return { ...s, Z, chaininess: singles / late.length, top: Z[Z.length - 1].height }
  }),
)
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div v-for="t in trees" :key="t.m" class="col">
        <Dendro
          :Z="t.Z" :color-of="() => t.color" :width="0.9" :y-label="t.m === 'single' ? 'merge distance' : ''"
          :title="`${t.title}<br><span style='font-weight:400;font-size:0.76rem'>${t.sub}</span>`"
          :title-color="t.color"
        />
        <div class="note">{{ t.cap }}<br />late merges adding one point: {{ (t.chaininess * 100).toFixed(0) }}%</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="noise" :min="0" :max="80" :step="1" label="stray points added" :digits="0" :color="RED" />
      <Knob v-model="n" :min="40" :max="200" :step="10" label="points in the clusters" :digits="0" :color="BLUE" />
      <Readout
        :items="[
          { label: 'single: late merges adding one point', value: `${(trees[0].chaininess * 100).toFixed(0)}%`, color: BLUE },
          { label: 'Ward', value: `${(trees[3].chaininess * 100).toFixed(0)}%`, color: PURPLE },
        ]"
      />
      <span class="note">a tree whose last merges keep swallowing one more
        point is a chain, which is single linkage's failure mode</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.9rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.col .note { text-align: center; line-height: 1.4; }
.controls { display: flex; gap: 1.3rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
</style>
