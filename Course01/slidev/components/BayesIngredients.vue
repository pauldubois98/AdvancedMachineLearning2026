<!-- bayes_ingredients: priors, class densities and the posterior they give;
     the decision threshold is where the posteriors cross. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { npdf } from '../lib/stats'
import { BLUE, INK, PURPLE, RED } from '../lib/theme'

const pi1 = ref(0.65)
const m2 = ref(2)
const s2 = ref(1.4)
const post1 = (x: number) => { const a = pi1.value * npdf(x, -1.2, 1.1), b = (1 - pi1.value) * npdf(x, m2.value, s2.value); return a / (a + b) }
const cuts = computed(() => {
  const out: number[] = []
  let prev = post1(-5) - 0.5
  for (let i = 1; i <= 1100; i++) { const x = -5 + i / 100; const v = post1(x) - 0.5; if (Math.sign(v) !== Math.sign(prev)) out.push(x); prev = v }
  return out
})
const top = computed(() => Math.max(npdf(0, 0, 1.1), npdf(0, 0, s2.value)) * 1.1)
</script>

<template>
  <div class="cmp">
    <div class="r3">
      <LineChart :series="[]" :bars="[{ x: 0, y: pi1, w: 0.55, color: BLUE, alpha: 0.9, label: pi1.toFixed(2) }, { x: 1, y: 1 - pi1, w: 0.55, color: RED, alpha: 0.9, label: (1 - pi1).toFixed(2) }]"
        :x-domain="[-0.6, 1.6]" :y-domain="[0, 1.05]" :y-ticks="[0, 0.25, 0.5, 0.75, 1]" title="priors πₖ: class 1, class 2" :title-color="BLUE" />
      <LineChart :series="[{ points: curve((x) => npdf(x, -1.2, 1.1), -5, 6), color: BLUE }, { points: curve((x) => npdf(x, m2, s2), -5, 6), color: RED }]"
        :x-domain="[-5, 6]" :y-domain="[0, top]" :x-ticks="[-4, -2, 0, 2, 4, 6]" :y-ticks="[]" x-label="x" title="densities fₖ(x)" :title-color="RED" />
      <LineChart :series="[{ points: curve(post1, -5, 6, 500), color: BLUE }, { points: curve((x) => 1 - post1(x), -5, 6, 500), color: RED }]"
        :x-domain="[-5, 6]" :y-domain="[0, 1.05]" :x-ticks="[-4, -2, 0, 2, 4, 6]" :y-ticks="[0, 0.5, 1]" x-label="x"
        :vlines="cuts.map((c) => ({ x: c, color: INK, dash: '6,4' }))" title="posterior P(C = k | x)" :title-color="PURPLE" />
    </div>
    <div class="foot">P(C = k | x) = fₖ(x) πₖ / Σᵢ fᵢ(x) πᵢ. Decide class 1 where the blue posterior is above ½: <b>{{ cuts.length ? cuts.map((c) => `x = ${c.toFixed(2)}`).join(', ') : 'no crossing' }}</b>. A larger prior pushes the threshold into the other class; a wider class 2 makes it win on both sides.</div>
    <div class="controls">
      <Knob v-model="pi1" :min="0.02" :max="0.98" :step="0.01" label="prior π₁" :color="BLUE" />
      <Knob v-model="m2" :min="-1" :max="4" :step="0.02" label="class 2 mean" :color="RED" />
      <Knob v-model="s2" :min="0.4" :max="3" :step="0.02" label="class 2 sd" :color="RED" />
    </div>
  </div>
</template>
