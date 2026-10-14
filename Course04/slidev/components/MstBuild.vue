<!-- mst_build: Prim's algorithm, edge by edge. The slider is how many edges
     the tree has taken; the dotted lines are the exits it could still use. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { distances, mstToy } from '../lib/data4'
import { primMst } from '../lib/density'
import { BLUE, GREEN, GRID, INK, MUTED } from '../lib/theme'

const m = ref(1)
const { X, names } = mstToy()
const D = distances(X)
const edges = primMst(D)

const inside = computed(() => {
  const s = new Set([0])
  edges.slice(0, m.value).forEach((e) => s.add(e.j))
  return s
})
const taken = computed(() => edges.slice(0, m.value - 1))
const current = computed(() => edges[m.value - 1])
/** every exit edge the tree could still take, from the tree before this step */
const options = computed(() => {
  const prev = new Set([0])
  edges.slice(0, m.value - 1).forEach((e) => prev.add(e.j))
  const out: { a: [number, number]; b: [number, number]; color: string; width: number; dash: number[]; alpha: number }[] = []
  for (const i of prev) {
    for (let j = 0; j < X.length; j++) {
      if (prev.has(j)) continue
      out.push({ a: X[i] as [number, number], b: X[j] as [number, number], color: GRID, width: 0.7, dash: [2, 3], alpha: 0.8 })
    }
  }
  return out
})
const total = computed(() => edges.slice(0, m.value).reduce((s, e) => s + e.w, 0))
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :point-size="9" :colors="X.map((_, i) => (inside.has(i) ? '#dde3ea' : '#f2f3f5'))"
      :domain="[-0.7, 4.4, -0.6, 3.2]"
      :edges="[
        ...options,
        ...taken.map((e) => ({ a: X[e.i] as [number, number], b: X[e.j] as [number, number], color: BLUE, width: 2 })),
        { a: X[current.i] as [number, number], b: X[current.j] as [number, number], color: GREEN, width: 2.6 },
      ]"
      :tags="[
        ...names.map((nm, i) => ({ x: X[i][0], y: X[i][1], text: nm, color: inside.has(i) ? INK : MUTED, size: 11, dy: 0 })),
        { x: (X[current.i][0] + X[current.j][0]) / 2, y: (X[current.i][1] + X[current.j][1]) / 2 + 0.22, text: current.w.toFixed(2), color: GREEN, size: 11 },
      ]"
      :title="m === 1 ? 'start anywhere, then add the cheapest exit edge' : `${m} edge${m > 1 ? 's' : ''} taken`"
      :title-color="BLUE"
    />
    <div class="right">
      <table class="plain narrow">
        <tr><th>step</th><th>edge</th><th>weight</th></tr>
        <tr v-for="(e, i) in edges" :key="i" :class="{ on: i === m - 1, off: i >= m }">
          <td>{{ i + 1 }}</td>
          <td>{{ names[e.i] }} – {{ names[e.j] }}</td>
          <td>{{ e.w.toFixed(2) }}</td>
        </tr>
      </table>
      <Knob v-model="m" :min="1" :max="6" :step="1" label="edges taken" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'total weight so far', value: total.toFixed(2), color: BLUE },
          { label: 'stops at n − 1', value: `${edges.length} edges`, color: MUTED },
        ]"
      />
      <p class="note">No cycle can ever appear, because the new endpoint is
        always chosen outside the tree. That is the whole proof, and it is why
        the result is a tree and not just a cheap subgraph.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 1.5rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.on td { background: #eefaef; font-weight: 600; color: #00ab0e; }
.off td { color: #cccfd2; }
</style>
