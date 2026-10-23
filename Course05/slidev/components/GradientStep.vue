<!-- gradient_negative: one entry H_kj whose parabola has its vertex below
     zero. A plain gradient step can cross zero, a projection lands exactly
     on 0 and stays there, the multiplicative step only rescales. Five steps
     of each, from the same start. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { range } from '../lib/losses'
import { GREEN, INK, PURPLE, RED } from '../lib/theme'

// F(h) = ½(x - w h - s)², x = 1, w = 1, s = 1.4: vertex at h = -0.4
const x = 1, w = 1, s = 1.4
const F = (h: number) => 0.5 * (x - w * h - s) ** 2
const dF = (h: number) => w * (w * h + s - x)
const h0 = ref(1.3)
const eta = ref(1.2)
const hs = range(-1.1, 1.8, 160)
function path(next: (h: number) => number) {
  const out = [h0.value]
  for (let t = 0; t < 5; t++) out.push(next(out[out.length - 1]))
  return out
}
const plain = computed(() => path((h) => h - eta.value * dF(h)))
const proj = computed(() => path((h) => Math.max(0, h - eta.value * dF(h))))
// split ∇ = w(wh + s) - w x, both parts >= 0: h <- h x / (wh + s)
const mu = computed(() => path((h) => (h * x) / (w * h + s)))
const panels = computed(() => [
  { name: 'plain gradient step', color: RED, path: plain.value, cap: 'the step can cross zero' },
  { name: 'project back', color: PURPLE, path: proj.value, cap: 'cheap, but it kills the information in the step' },
  { name: 'rescale (multiplicative)', color: GREEN, path: mu.value, cap: 'multiply by something positive: zero is unreachable' },
])
const segs = (p: number[]) => p.slice(0, -1).map((a, i) => ({ points: [[a, F(a)], [p[i + 1], F(p[i + 1])]] as [number, number][], color: '', width: 1.6 }))
</script>

<template>
  <div class="wrap">
    <div class="note top">The constraint H ≥ 0 is what rules out plain gradient descent.</div>
    <div class="panels">
      <div v-for="p in panels" :key="p.name" class="col">
        <LineChart
          :series="[{ points: hs.map((h) => [h, F(h)]), color: '#9aa0a6', width: 1.6 }, ...segs(p.path).map((sg) => ({ ...sg, color: p.color }))]"
          :bands="[{ x0: -1.1, x1: 0, color: '#edeef0', alpha: 1 }]"
          :dots="p.path.map((h, i) => ({ x: h, y: F(h), color: i ? p.color : '#1b1b1b', r: i ? 3.5 : 5 }))"
          :labels="[{ x: -0.55, y: 2.4, text: 'forbidden', color: '#9aa0a6', size: 12 }]"
          :x-domain="[-1.1, 1.8]" :y-domain="[0, 2.6]" x-label="H_kj" :x-ticks="[0]" :y-ticks="[]"
          :title="p.name" :title-color="p.color"
        />
        <div class="cap">{{ p.cap }}<br><span class="vals">{{ p.path.map((h) => h.toFixed(2)).join(' → ') }}</span></div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="h0" :min="0.1" :max="1.7" :step="0.01" label="start H_kj" :color="INK" />
      <Knob v-model="eta" :min="0.1" :max="2" :step="0.01" label="step size η" :color="RED" />
      <span class="note">The multiplicative rule has no η: its step is chosen per entry.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.panels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.4rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; line-height: 1.4; }
.vals { color: #4a4a4a; font-variant-numeric: tabular-nums; font-size: 0.7rem; }
</style>
