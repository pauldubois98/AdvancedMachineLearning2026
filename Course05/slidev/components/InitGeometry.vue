<!-- init_geometry: a cloud made of two arms, r = 2. The two columns of W are
     rays from the origin; each start puts them somewhere else. Slide the
     number of MU passes and watch where each start ends up. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { arms } from '../lib/data5'
import { type Init, fit, init, lossOf } from '../lib/nmf'
import { BLUE, GOLD, GREEN, INK, RED } from '../lib/theme'

const passes = ref(0)
const pts = Array.from({ length: arms.c }, (_, j) => [arms.a[j], arms.a[arms.c + j]] as [number, number])
// the first seed that draws both columns from the same arm, as the printed
// figure does: the columns of W₀ are then two points of X itself
const armOf = (v: number, w: number) => {
  let best = 0, bd = Infinity
  pts.forEach(([x, y], j) => { const d = (x - v) ** 2 + (y - w) ** 2; if (d < bd) { bd = d; best = j } })
  return best < arms.c / 2 ? 0 : 1
}
const same = (() => {
  for (let s = 0; s < 200; s++) {
    const W = init(arms, 2, 'cols', s).W
    if (armOf(W.a[0], W.a[2]) === armOf(W.a[1], W.a[3])) return s
  }
  return 0
})()
const strategies: { name: string; color: string; how: Init; seed: number; cap: string }[] = [
  { name: 'constants', color: RED, how: 'constant', seed: 0, cap: 'one single ray: MU can never break the tie' },
  { name: 'random', color: GOLD, how: 'random', seed: 0, cap: 'two arbitrary rays, with no relation to the data' },
  { name: 'NNDSVD', color: GREEN, how: 'nndsvd', seed: 0, cap: 'deterministic: the mean direction, then the next one' },
  { name: 'r columns of X', color: GREEN, how: 'cols', seed: same, cap: 'two real data points, here both from the same arm' },
  { name: 'k-means', color: BLUE, how: 'kmeans', seed: 0, cap: 'one centroid per cluster: the rays land on the arms' },
]
const starts = strategies.map((s) => init(arms, 2, s.how, s.seed))
const panels = computed(() => strategies.map((s, i) => {
  const f = fit(arms, starts[i], passes.value)
  const rays = [0, 1].map((k) => {
    const v = [f.W.a[k], f.W.a[2 + k]]
    const n = Math.hypot(v[0], v[1]) || 1
    return { points: [[0, 0], [(1.45 * v[0]) / n, (1.45 * v[1]) / n]] as [number, number][], color: s.color, width: 2.6 }
  })
  return { ...s, rays, loss: lossOf(arms, f) }
}))
</script>

<template>
  <div class="wrap">
    <div class="note top">Columns of W, as rays from the origin</div>
    <div class="panels">
      <div v-for="p in panels" :key="p.name" class="col">
        <LineChart
          :series="p.rays" :dots="pts.map(([x, y]) => ({ x, y, color: '#9aa0a6', r: 2 }))"
          :x-domain="[0, 1.5]" :y-domain="[0, 1.5]" :x-ticks="[]" :y-ticks="[]" :title="p.name" :title-color="p.color"
        />
        <div class="cap">{{ p.cap }}</div>
        <div class="loss">loss {{ p.loss.toFixed(2) }}</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="passes" :min="0" :max="300" :step="1" label="MU passes" :digits="0" :color="INK" />
      <span class="note">r = 2 on a cloud of two arms. Constants stay a single ray forever; k-means starts where the others end.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.panels { display: grid; grid-template-columns: repeat(5, 1fr); gap: 1rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto auto; gap: 0.2rem; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.72rem; line-height: 1.35; }
.loss { text-align: center; font-size: 0.75rem; font-variant-numeric: tabular-nums; }
</style>
