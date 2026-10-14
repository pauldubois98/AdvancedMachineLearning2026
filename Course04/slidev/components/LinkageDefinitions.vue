<!-- linkage_definitions: four answers to "how far apart are two groups?".
     The slider slides the right-hand group away, and all four numbers move
     at once, which is the point: they do not agree. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { groupDistances } from '../lib/hier'
import { BLUE, GREEN, PURPLE, RED, INK, MUTED } from '../lib/theme'

const gap = ref(2.7)
const show = ref('single')

const A = (() => {
  const rng = new Rng(11)
  return Array.from({ length: 14 }, () => [rng.normal(-1.25, 0.42), rng.normal(0.25, 0.42)])
})()
const B0 = (() => {
  const rng = new Rng(29)
  return Array.from({ length: 14 }, () => [rng.normal(0, 0.42), rng.normal(-0.25, 0.42)])
})()
const B = computed(() => B0.map((p) => [p[0] - 1.25 + gap.value, p[1]]))
const g = computed(() => groupDistances(A, B.value))
const X = computed(() => A.concat(B.value))
const mean = (P: number[][]) => [
  P.reduce((s, p) => s + p[0], 0) / P.length,
  P.reduce((s, p) => s + p[1], 0) / P.length,
]

const edges = computed(() => {
  const d = g.value
  if (show.value === 'single') {
    return [{ a: A[d.minPair[0]] as [number, number], b: B.value[d.minPair[1]] as [number, number], color: BLUE, width: 2.4 }]
  }
  if (show.value === 'complete') {
    return [{ a: A[d.maxPair[0]] as [number, number], b: B.value[d.maxPair[1]] as [number, number], color: RED, width: 2.4 }]
  }
  if (show.value === 'average') {
    const out: { a: [number, number]; b: [number, number]; color: string; width: number; alpha: number }[] = []
    A.forEach((a, i) => {
      if (i % 3) return
      B.value.forEach((b, j) => {
        if (j % 3) return
        out.push({ a: a as [number, number], b: b as [number, number], color: GREEN, width: 0.6, alpha: 0.35 })
      })
    })
    return out
  }
  return [{ a: mean(A) as [number, number], b: mean(B.value) as [number, number], color: PURPLE, width: 2.4 }]
})
const crosses = computed(() =>
  show.value === 'centroid' || show.value === 'ward'
    ? [
        { x: mean(A)[0], y: mean(A)[1], color: PURPLE },
        { x: mean(B.value)[0], y: mean(B.value)[1], color: PURPLE },
      ]
    : [],
)
const rows = computed(() => [
  { key: 'single', name: 'single / MIN', formula: 'minₓ,ᵧ D(x, y)', value: g.value.single, color: BLUE },
  { key: 'complete', name: 'complete / MAX', formula: 'maxₓ,ᵧ D(x, y)', value: g.value.complete, color: RED },
  { key: 'average', name: 'average', formula: '(1 / nᵢnⱼ) ΣΣ D(x, y)', value: g.value.average, color: GREEN },
  { key: 'centroid', name: 'centroid', formula: 'D(mᵢ, mⱼ)', value: g.value.centroid, color: PURPLE },
])
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :labels="X.map((_, i) => (i < 14 ? -2 : -2))" :colors="X.map(() => INK)"
      :point-size="4.2" :point-alpha="0.6" :edges="edges" :crosses="crosses"
      :domain="[-3, 6.4, -2.1, 2.1]"
      title="How far apart are two groups of points?" :title-color="MUTED"
    />
    <div class="right">
      <table class="plain">
        <tr><th>linkage</th><th>definition</th><th>value</th></tr>
        <tr
          v-for="r in rows" :key="r.key" class="row" :class="{ on: show === r.key }"
          @click="show = r.key"
        >
          <td :style="{ color: r.color, fontWeight: 600 }">{{ r.name }}</td>
          <td class="note">{{ r.formula }}</td>
          <td :style="{ color: r.color, fontWeight: 600 }">{{ r.value.toFixed(2) }}</td>
        </tr>
      </table>
      <div class="controls">
        <Choice
          v-model="show" label="show"
          :options="rows.map((r) => ({ value: r.key, label: r.name.split(' ')[0], color: r.color }))"
        />
        <Knob v-model="gap" :min="1.2" :max="5.5" label="distance between the groups" :color="INK" />
        <Readout
          :items="[
            { label: 'max / min', value: (g.complete / g.single).toFixed(1) + '×', color: RED },
            { label: 'Ward, 14 vs 14', value: g.ward.toFixed(2), color: PURPLE },
          ]"
        />
      </div>
      <p class="note">Click a row to draw what it measures. The four numbers
        rank pairs of clusters differently, so the whole tree changes with the
        choice.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.6rem; justify-content: center; }
.row { cursor: pointer; }
.row.on td { background: #f4f6f8; }
.controls { display: flex; flex-direction: column; gap: 0.45rem; }
</style>
