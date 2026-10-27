<!-- posterior_curve: the same computation at every point of the axis. The
     prior p1 moves the boundary: a rarer class must be more likely to win. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ANIMALS, ANIMAL_FIT, linspace, resp1 } from '../lib/gmm'
import { curve, edges, stacked } from '../lib/charts'
import { BLUE, COMP, MUTED, PURPLE } from '../lib/theme'

const p1 = ref(+ANIMAL_FIT.p[0].toFixed(2))
const m = computed(() => ({ ...ANIMAL_FIT, p: [p1.value, 1 - p1.value] }))
const grid = linspace(80, 99, 500)
const cut = computed(() => {
  let best = grid[0]
  let d = Infinity
  for (const x of linspace(84, 95, 1100)) { const v = Math.abs(resp1(x, m.value)[0] - 0.5); if (v < d) { d = v; best = x } }
  return best
})
const groups = computed(() => {
  const g: number[][] = [[], []]
  for (const x of ANIMALS) g[resp1(x, m.value)[0] > 0.5 ? 0 : 1].push(x)
  return g
})
</script>

<template>
  <div class="wrap">
    <div class="note top">The same computation at every point of the axis</div>
    <div class="body">
      <div class="left">
        <LineChart
          :series="[]" :bars="stacked(groups, edges(81.5, 98.5, 1), COMP, { alpha: 0.8 })"
          :vlines="[{ x: cut, color: MUTED, dash: '5 4' }]"
          :x-domain="[80, 99]" :y-domain="[0, 62]" :x-ticks="[]" :y-ticks="[]" y-label="most likely class" :unit-height="200"
        />
        <LineChart
          :series="[0, 1].map((k) => ({ points: curve(grid, (x) => resp1(x, m)[k]), color: COMP[k], width: 2.4 }))"
          :hlines="[{ y: 0.5, dash: '2 3' }]" :vlines="[{ x: cut, color: MUTED, dash: '5 4' }]"
          :labels="[{ x: cut - 0.3, y: 0.2, text: `boundary ${cut.toFixed(1)} mm`, color: MUTED, anchor: 'end', size: 12 }]"
          :x-domain="[80, 99]" :y-domain="[0, 1.03]" x-label="length (mm)" :x-ticks="[82, 86, 90, 94, 98]" :y-ticks="[0, 0.5, 1]" :unit-height="200"
        />
      </div>
      <div class="side">
        <div class="h" :style="{ color: BLUE }">Pointwise</div>
        <p>— each x gets its own probabilities, summing to 1</p>
        <p>— classify: pick the larger one</p>
        <p>— boundary: where they are equal</p>
        <p>— near it, the call is uncertain</p>
        <p class="note" style="margin-top: 0.8rem">Moving the prior p₁ moves the boundary. And it all needs the parameters, which we do not have yet.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="p1" :min="0.02" :max="0.98" :step="0.01" label="prior p₁" :color="PURPLE" />
      <span class="note">means and widths are the fitted ones; {{ ANIMAL_FIT.p[0].toFixed(2) }} is the fitted p₁</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.6fr 1fr; gap: 2rem; min-height: 0; }
.left { display: grid; grid-template-rows: 1fr 1fr; gap: 0.3rem; min-height: 0; }
.side { align-self: center; }
</style>
