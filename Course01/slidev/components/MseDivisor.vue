<!-- mse_divisor: the error of S/c as a function of c, exact for Gaussian data:
     S ~ σ² χ²(n−1), so bias² and variance are closed forms. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const n = ref(8)
const lo = computed(() => Math.max(1, n.value - 3))
const hi = computed(() => n.value * 1.8 + 1)
const parts = (c: number) => {
  const k = n.value - 1
  const b2 = (k / c - 1) ** 2, v = (2 * k) / (c * c)
  return { b2, v, mse: b2 + v }
}
const line = (key: 'b2' | 'v' | 'mse') => Array.from({ length: 300 }, (_, i) => {
  const c = lo.value + ((hi.value - lo.value) * i) / 299
  return [c, parts(c)[key]] as [number, number]
})
const ymax = computed(() => Math.min(parts(n.value - 1).mse * 1.8, 2.5))
const marks = computed(() => [
  { c: n.value - 1, color: BLUE, name: 'unbiased' },
  { c: n.value, color: GREEN, name: 'MLE' },
  { c: n.value + 1, color: PURPLE, name: 'shrunk' },
])
const ticks = computed(() => { const s = n.value < 12 ? 2 : n.value < 30 ? 5 : 10; const out = []; for (let v = Math.ceil(lo.value / s) * s; v <= hi.value; v += s) out.push(v); return out })
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Exact, not simulated:</b> for n Gaussian points, S = Σ (xᵢ − x̄)² follows σ² χ²(n − 1), so S / c has bias² = σ⁴ ((n − 1)/c − 1)² and variance 2 (n − 1) σ⁴ / c². Here σ² = 1.</div>
    <LineChart :series="[{ points: line('v'), color: GOLD, dash: '7,4' }, { points: line('b2'), color: RED, dash: '7,4' }, { points: line('mse'), color: INK, width: 3 }]"
      :x-domain="[lo, hi]" :y-domain="[0, ymax]" :x-ticks="ticks" :y-ticks="[0, 0.1, 0.2, 0.3, 0.4, 0.5, 1, 1.5, 2].filter((t) => t <= ymax)" x-label="the divisor c" y-label="error on σ²"
      :dots="marks.map((m) => ({ x: m.c, y: parts(m.c).mse, color: m.color, r: 6 }))"
      :labels="[...marks.map((m, k) => ({ x: m.c, y: parts(m.c).mse + ymax * (0.06 + 0.06 * k), text: `${m.name}, c = ${m.c}`, color: m.color, anchor: 'middle', size: 12 })),
        { x: hi, y: parts(hi).v + ymax * 0.03, text: 'variance', color: GOLD, anchor: 'end' }, { x: hi, y: parts(hi).b2 + ymax * 0.03, text: 'bias²', color: RED, anchor: 'end' }, { x: hi, y: parts(hi).mse + ymax * 0.03, text: 'MSE', color: INK, anchor: 'end' }]" />
    <div class="foot">raising c shrinks the variance and grows the bias; the sum is smallest at c = n + 1 = <b :style="{ color: PURPLE }">{{ n + 1 }}</b>, MSE <b :style="{ color: PURPLE }">{{ parts(n + 1).mse.toFixed(3) }}</b> vs <b :style="{ color: BLUE }">{{ parts(n - 1).mse.toFixed(3) }}</b> for the unbiased one</div>
    <div class="controls"><Knob v-model="n" :min="2" :max="40" :step="1" :digits="0" label="n" :color="INK" /></div>
  </div>
</template>
