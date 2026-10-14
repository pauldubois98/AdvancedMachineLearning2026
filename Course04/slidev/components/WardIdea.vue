<!-- ward_idea: the cost of a merge. Two small close clusters are cheaper to
     join than one of them with a big neighbour, even when the big one has
     points that sit nearer. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { wardCost } from '../lib/hier'
import { BLUE, GOLD, GREEN, RED, INK } from '../lib/theme'

const nA = ref(60)
const nB = ref(25)
const nC = ref(25)

const build = computed(() => {
  const rng = new Rng(6)
  const groups: { name: string; centre: [number, number]; sd: number; n: number; color: string }[] = [
    { name: 'A', centre: [-2.0, -0.6], sd: 0.45, n: nA.value, color: BLUE },
    { name: 'B', centre: [0.4, 1.3], sd: 0.35, n: nB.value, color: GREEN },
    { name: 'C', centre: [2.3, -0.8], sd: 0.35, n: nC.value, color: GOLD },
  ]
  const X: number[][] = []
  const labels: number[] = []
  groups.forEach((g, k) => {
    for (let i = 0; i < g.n; i++) {
      X.push([rng.normal(g.centre[0], g.sd), rng.normal(g.centre[1], g.sd)])
      labels.push(k)
    }
  })
  const means = groups.map((g, k) => {
    const pts = X.filter((_, i) => labels[i] === k)
    return [
      pts.reduce((s, p) => s + p[0], 0) / pts.length,
      pts.reduce((s, p) => s + p[1], 0) / pts.length,
    ]
  })
  return { X, labels, groups, means }
})

const pairs = computed(() => {
  const { groups, means } = build.value
  const mk = (i: number, j: number, color: string) => {
    const d = Math.hypot(means[i][0] - means[j][0], means[i][1] - means[j][1])
    return {
      key: `${groups[i].name}${groups[j].name}`,
      cost: wardCost(groups[i].n, groups[j].n, d),
      d,
      color,
      a: means[i] as [number, number],
      b: means[j] as [number, number],
    }
  }
  return [mk(1, 2, GREEN), mk(0, 1, RED), mk(0, 2, GOLD)]
})
const cheapest = computed(() => pairs.value.reduce((a, b) => (b.cost < a.cost ? b : a)))
/** the nearest single pair of points across A and B: what single linkage sees */
const nearestAB = computed(() => {
  const { X, labels } = build.value
  let best = { d: Infinity, a: [0, 0] as [number, number], b: [0, 0] as [number, number] }
  X.forEach((p, i) => {
    if (labels[i] !== 0) return
    X.forEach((q, j) => {
      if (labels[j] !== 1) return
      const d = Math.hypot(p[0] - q[0], p[1] - q[1])
      if (d < best.d) best = { d, a: p as [number, number], b: q as [number, number] }
    })
  })
  return best
})
const nearestBC = computed(() => {
  const { X, labels } = build.value
  let best = Infinity
  X.forEach((p, i) => {
    if (labels[i] !== 1) return
    X.forEach((q, j) => {
      if (labels[j] !== 2) return
      best = Math.min(best, Math.hypot(p[0] - q[0], p[1] - q[1]))
    })
  })
  return best
})
const dom: [number, number, number, number] = [-4.0, 4.2, -2.6, 3.0]
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="build.X" :labels="build.labels" :point-size="2.6" :domain="dom"
      :edges="pairs.map((p) => ({ a: p.a, b: p.b, color: p.color, width: p.key === cheapest.key ? 2.4 : 1.2, dash: [5, 4] }))"
      :crosses="build.means.map((m, k) => ({ x: m[0], y: m[1], color: build.groups[k].color }))"
      :tags="[
        ...build.groups.map((g, k) => ({ x: build.means[k][0], y: build.means[k][1] + (k === 1 ? 0.75 : -1.2), text: `${g.name} (n = ${g.n})`, color: g.color, size: 12 })),
        ...pairs.map((p) => ({ x: (p.a[0] + p.b[0]) / 2, y: (p.a[1] + p.b[1]) / 2 + 0.26, text: `ΔJ_w = ${p.cost.toFixed(0)}`, color: p.color, size: 11.5 })),
      ]"
      title="Ward: merge whatever costs the least inertia" :title-color="GREEN"
    />
    <div class="right">
      <div class="formula"><Tex display formula='\Delta J_w = \frac{n_i n_j}{n_i + n_j}\, D^2(m_i, m_j)' /></div>
      <table class="plain">
        <tr><th>merge</th><th>centre gap</th><th>ΔJ<sub>w</sub></th></tr>
        <tr v-for="p in pairs" :key="p.key">
          <td :style="{ color: p.color, fontWeight: 600 }">{{ p.key }}</td>
          <td>{{ p.d.toFixed(2) }}</td>
          <td :style="{ color: p.key === cheapest.key ? GREEN : INK, fontWeight: p.key === cheapest.key ? 600 : 400 }">
            {{ p.cost.toFixed(0) }}{{ p.key === cheapest.key ? '  ← taken' : '' }}
          </td>
        </tr>
      </table>
      <div class="controls">
        <Knob v-model="nA" :min="5" :max="120" :step="1" label="n of A" :digits="0" :color="BLUE" />
        <Knob v-model="nB" :min="5" :max="120" :step="1" label="n of B" :digits="0" :color="GREEN" />
        <Knob v-model="nC" :min="5" :max="120" :step="1" label="n of C" :digits="0" :color="GOLD" />
      </div>
      <Readout
        :items="[
          { label: 'nearest A-B pair of points', value: nearestAB.d.toFixed(2), color: RED },
          { label: 'nearest B-C pair', value: nearestBC.toFixed(2), color: GREEN },
        ]"
      />
      <p class="note">Single linkage would compare the two numbers above and
        merge A with B. Ward compares the inertia a merge adds, so sizes count:
        make A small enough and the answer flips.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.formula { text-align: center; font-size: 0.86rem; }
.controls { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.6rem; }
</style>
