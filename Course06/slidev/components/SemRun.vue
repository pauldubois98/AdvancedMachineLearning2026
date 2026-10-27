<!-- sem_run: stochastic EM on the same data. It finds the two modes, then
     keeps jittering: the labels are redrawn at every pass. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, em1, linspace, sem1, weighted1 } from '../lib/gmm'
import { bars, curve, edges, fmt, stacked } from '../lib/charts'
import { COMP, GOLD, GREEN, INK, MUTED } from '../lib/theme'

const T = 60
const seed = ref(5)
const t = ref(40)
const start = { p: [0.5, 0.5], mu: [87.5, 90.5], sd: [3, 3] }
const hist = computed(() => sem1(ANIMALS, start, T, { seed: seed.value }))
const emTr = em1(ANIMALS, start, T).map((h, i) => [i, h.ll] as [number, number])
const cur = computed(() => hist.value[t.value])
const E = edges(81.5, 98.5, 1)
const theBars = computed(() => {
  const z = cur.value.z
  if (!z) return bars(ANIMALS, E, { density: true })
  const g: number[][] = [[], []]
  ANIMALS.forEach((x, i) => g[z[i]].push(x))
  return stacked(g, E, COMP, { density: true, alpha: 0.6 })
})
const grid = linspace(80, 99, 400)
const tr = computed(() => hist.value.map((h, i) => [i, h.ll] as [number, number]))
const late = computed(() => hist.value.slice(25).map((h) => h.ll))
</script>

<template>
  <div class="wrap">
    <div class="note top">Stochastic EM on the same data: it finds the two modes, then keeps jittering</div>
    <div class="body">
      <LineChart
        :series="[0, 1].map((k) => ({ points: curve(grid, (x) => weighted1(x, cur)[k]), color: COMP[k], width: 2.2 }))"
        :bars="theBars" :x-domain="[80, 99]" :y-domain="[0, 0.16]" x-label="length (mm)" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[]"
        :title="`t = ${t}: ℓ = ${fmt(cur.ll)}`" :title-color="t ? INK : MUTED"
      />
      <div class="right">
        <LineChart
          :series="[{ points: emTr, color: GREEN, width: 1.6, dash: '5 4' }, { points: tr, color: GOLD, width: 2.2 }]"
          :dots="[{ x: t, y: cur.ll, color: GOLD, r: 5 }]"
          :labels="[{ x: 42, y: -1000, text: 'SEM', color: GOLD, size: 13 }, { x: 42, y: -985, text: 'EM', color: GREEN, size: 13 }]"
          :x-domain="[0, T]" :y-domain="[-1020, -940]" x-label="pass t" y-label="ℓ_obs" :x-ticks="[0, 20, 40, 60]" :y-ticks="[-1000, -960]"
          :unit-height="260"
        />
        <p class="note">Colours are the drawn labels, redrawn every pass. Past pass 25 the log-likelihood still rattles in [{{ fmt(Math.min(...late), 1) }}, {{ fmt(Math.max(...late), 1) }}] instead of settling.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="t" :min="0" :max="T" :step="1" label="pass t" :digits="0" :color="GOLD" />
      <Knob v-model="seed" :min="1" :max="60" :step="1" label="seed" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 2rem; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
</style>
