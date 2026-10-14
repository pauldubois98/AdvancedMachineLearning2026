<!-- additive_model: what F_m IS. One row of the data, its leaf value in every
     tree, and the running sum those add up to. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sine1d } from '../lib/databis'
import { fitBooster } from '../lib/boost'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const eta = ref(0.3)
const row = ref(20)
const shown = ref(5)
const MAX = 40
const data = sine1d(70, 0.2, 3)

const model = computed(() =>
  fitBooster(data.X, data.y, {
    nTrees: MAX, eta: eta.value, maxDepth: 2, loss: 'squared', seed: 0,
  }),
)
const x = computed(() => data.x[Math.round(row.value)])
const ledger = computed(() => {
  const m = model.value
  const out: { name: string; leaf: number; step: number; total: number }[] = []
  let F = m.f0
  out.push({ name: 'F₀', leaf: NaN, step: m.f0, total: F })
  for (let t = 0; t < Math.round(shown.value); t++) {
    const w = m.trees[t].predict([x.value])[0]
    F += eta.value * w
    out.push({ name: `h${t + 1}`, leaf: w, step: eta.value * w, total: F })
  }
  return out
})
const finalF = computed(() => model.value.raw([x.value]))
const target = computed(() => data.y[Math.round(row.value)])
const curve = computed(() => {
  const pts: [number, number][] = []
  for (let i = 0; i <= 200; i++) {
    const v = i / 200
    pts.push([v, model.value.raw([v], Math.round(shown.value))])
  }
  return pts
})
</script>

<template>
  <div class="wrap">
    <div class="left">
      <LineChart
        :series="[{ points: curve, color: RED, width: 2.4 }]"
        :dots="[
          ...data.x.map((v, i) => ({ x: v, y: data.y[i], color: BLUE, r: 2.6 })),
          { x, y: target, color: '#1b1b1b', r: 6, hollow: true },
        ]"
        :vlines="[{ x, color: '#1b1b1b', dash: '3,3' }]"
        :x-domain="[0, 1]" :y-domain="[-1.9, 1.9]" :x-ticks="[0, 0.5, 1]" :y-ticks="[-1, 0, 1]"
        x-label="x" :title="`the sum after ${Math.round(shown)} trees`" :title-color="RED"
      />
      <div class="knobs">
        <Knob v-model="row" :min="0" :max="69" :step="1" label="which row" :digits="0" />
        <Knob v-model="shown" :min="0" :max="12" :step="1" label="trees added" :digits="0" :color="RED" />
        <Knob v-model="eta" :min="0.05" :max="1" label="η" :digits="2" :color="GREEN" />
      </div>
    </div>
    <div class="right">
      <table class="plain">
        <thead>
          <tr><th></th><th>what it fits</th><th>leaf it lands in</th><th>η × it</th><th>running F</th></tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in ledger" :key="i">
            <td :style="{ color: i ? BLUE : MUTED, fontWeight: 600 }">{{ r.name }}</td>
            <td class="why">{{ i === 0 ? 'the base rate (one constant)' : `what F${i - 1} got wrong` }}</td>
            <td>{{ isNaN(r.leaf) ? '·' : r.leaf.toFixed(3) }}</td>
            <td :style="{ color: BLUE }">{{ (r.step >= 0 ? '+' : '') + r.step.toFixed(3) }}</td>
            <td :style="{ fontWeight: 600 }">{{ r.total.toFixed(3) }}</td>
          </tr>
          <tr v-if="shown < MAX"><td colspan="5" class="dots">⋮ {{ MAX }} trees in total</td></tr>
        </tbody>
      </table>
      <Readout
        :items="[
          { label: 'all 40 trees give', value: finalF.toFixed(3), color: GREEN },
          { label: 'this row\'s y', value: target.toFixed(3) },
        ]"
      />
      <p class="note">
        F<sub>M</sub>(x) = F₀ + η h₁(x) + η h₂(x) + … + η h<sub>M</sub>(x). A tree
        contributes one number per row: the value of the single leaf that row falls into.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.15fr; gap: 1.6rem; height: 100%; min-height: 0; }
.left { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; min-height: 0; }
.right { display: flex; flex-direction: column; justify-content: center; gap: 0.6rem; }
.knobs { display: flex; flex-direction: column; gap: 0.3rem; }
.why { color: var(--muted); font-size: 0.78rem; }
.dots { color: var(--muted); text-align: center; }
td { font-variant-numeric: tabular-nums; }
.note { font-size: 0.78rem; margin: 0; color: var(--muted); line-height: 1.5; }
</style>
