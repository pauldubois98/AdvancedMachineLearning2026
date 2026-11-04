<!-- dartboard: estimates of a 2-D parameter thrown at the target. Bias moves
     the cloud off the cross, variance spreads it; the MSE adds both. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { circle } from '../lib/hist'
import { mean } from '../lib/stats'
import type { Pt } from '../lib/geom'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const bias = ref(0.4)
const spread = ref(0.3)
const r = new Rng(7)
const Z = Array.from({ length: 40 }, () => [r.normal(), r.normal()])
const ang = Math.atan2(0.35, 0.55)
const X = computed<Pt[]>(() => Z.map(([u, v]) => [bias.value * Math.cos(ang) + spread.value * u, bias.value * Math.sin(ang) + spread.value * v]))
const ctr = computed<Pt>(() => [mean(X.value.map((p) => p[0])), mean(X.value.map((p) => p[1]))])
const b2 = computed(() => ctr.value[0] ** 2 + ctr.value[1] ** 2)
const v = computed(() => mean(X.value.map((p) => (p[0] - ctr.value[0]) ** 2 + (p[1] - ctr.value[1]) ** 2)))
const rings = [...circle([0, 0], 1, '#d5d8dc', 1), ...circle([0, 0], 0.66, '#d5d8dc', 1), ...circle([0, 0], 0.33, '#d5d8dc', 1)]
const color = computed(() => (bias.value < 0.2 ? (spread.value < 0.25 ? GREEN : BLUE) : spread.value < 0.25 ? GOLD : RED))
const bars = computed(() => [
  { x: 0, y: b2.value, w: 0.6, color: RED, alpha: 0.8, label: b2.value.toFixed(2) },
  { x: 1, y: v.value, w: 0.6, color: BLUE, alpha: 0.8, label: v.value.toFixed(2) },
  { x: 2, y: b2.value + v.value, w: 0.6, color: PURPLE, alpha: 0.85, label: (b2.value + v.value).toFixed(2) },
])
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> 40 estimates of a 2-D parameter whose true value θ₀ is the cross. Each dot is the estimate from one sample. The bias pushes all of them the same way; the variance scatters them.</div>
    <div class="r23">
      <Plane :X="X" :colors="color" :size="4" :segments="rings" :domain="[-1.35, 1.35, -1.35, 1.35]"
        :markers="[{ at: [0, 0], color: INK, shape: 'x', size: 7 }, { at: ctr, color: INK, shape: 'ring', size: 5 }]" />
      <LineChart :series="[]" :bars="bars" :x-domain="[-0.6, 2.6]" :y-domain="[0, Math.max(1.4, (b2 + v) * 1.2)]" :y-ticks="[0, 0.5, 1, 1.5, 2].filter((t) => t <= Math.max(1.4, (b2 + v) * 1.2))" title="bias² + variance = MSE" />
    </div>
    <div class="foot">bars, left to right: <b :style="{ color: RED }">bias²</b> (cross to ring, the mean of the dots), <b :style="{ color: BLUE }">variance</b> (dots around their mean), <b :style="{ color: PURPLE }">MSE</b> (dots to the cross). The two problems are independent.</div>
    <div class="controls">
      <Knob v-model="bias" :min="0" :max="0.9" :step="0.01" label="bias" :color="RED" />
      <Knob v-model="spread" :min="0.02" :max="0.6" :step="0.01" label="spread" :color="BLUE" />
    </div>
  </div>
</template>
