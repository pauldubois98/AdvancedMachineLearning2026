<!-- dr_obstacles, noise features: two groups that two features separate,
     drowned by features that carry nothing. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { histogram, linspace } from '../lib/geom'
import { Rng } from '../lib/rng'
import { BLUE, GOLD, GREEN } from '../lib/theme'

const noise = ref(50)
const sd = ref(0.8)
const M = 300, N = 100
// the two features that matter (fixed), and M noise features drawn once
const r = new Rng(5)
const info = Array.from({ length: 2 * N }, (_, i) => { const c = i < N ? 0 : 3; return [c + r.normal(0, 0.5), c + r.normal(0, 0.5)] })
const Z = Array.from({ length: 2 * N }, () => Array.from({ length: M }, () => r.normal(0, 1)))
const n2 = 2 * N
const I2 = new Float64Array(n2 * n2)
for (let i = 0; i < n2; i++) for (let j = 0; j < n2; j++) I2[i * n2 + j] = (info[i][0] - info[j][0]) ** 2 + (info[i][1] - info[j][1]) ** 2
// the squared noise distance of every pair, summed over the first m features,
// kept at every grid value of m
const GRIDM = [0, 10, 20, 35, 50, 75, 100, 150, 200, 250, 300]
function noiseD(m: number) {
  const out = new Float64Array(n2 * n2)
  for (let i = 0; i < n2; i++) for (let j = i + 1; j < n2; j++) {
    let s = 0
    const a = Z[i], b = Z[j]
    for (let k = 0; k < m; k++) { const d = a[k] - b[k]; s += d * d }
    out[i * n2 + j] = s; out[j * n2 + i] = s
  }
  return out
}
const cache = new Map<number, Float64Array>()
// only the grid values are kept: the slider's own value is recomputed
const ND = (m: number) => { let v = cache.get(m); if (!v) { v = noiseD(m); if (GRIDM.includes(m)) cache.set(m, v) } return v }
/** the share of points whose nearest neighbour is in their own group */
function purity(m: number, s: number) {
  const nd = ND(m), s2 = s * s
  let ok = 0
  for (let i = 0; i < n2; i++) {
    let best = -1, bd = Infinity
    for (let j = 0; j < n2; j++) { if (j === i) continue; const d = I2[i * n2 + j] + s2 * nd[i * n2 + j]; if (d < bd) { bd = d; best = j } }
    if ((best < N) === (i < N)) ok++
  }
  return ok / n2
}
const m = computed(() => Math.round(noise.value))
const dists = (mm: number) => {
  const nd = ND(mm), s2 = sd.value ** 2, win: number[] = [], btw: number[] = []
  for (let i = 0; i < n2; i++) for (let j = i + 1; j < n2; j++) {
    const d = Math.sqrt(I2[i * n2 + j] + s2 * nd[i * n2 + j])
    if ((i < N) === (j < N)) win.push(d); else btw.push(d)
  }
  return { win, btw }
}
const now = computed(() => dists(m.value))
const ref0 = dists(0)
const E = computed(() => linspace(0, Math.max(...now.value.btw, ...now.value.win) * 1.05, 60))
function hist(v: number[], color: string, dash?: string) {
  const e = E.value, h = histogram(v, e), w = e[1] - e[0], tot = v.length * w
  return { points: h.flatMap((c, j) => [[e[j], c / tot], [e[j + 1], c / tot]] as [number, number][]), color, width: 2, dash }
}
const ymax = computed(() => Math.max(...[...hist(now.value.win, BLUE).points, ...hist(now.value.btw, GOLD).points].map((p) => p[1])) * 1.1)
const curve = computed(() => GRIDM.map((g) => [g, purity(g, sd.value)] as [number, number]))
const pNow = computed(() => purity(m.value, sd.value))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> two groups of 100 points that two useful features separate (centres 3 apart in each), plus extra features of pure Gaussian noise, drawn the same way for both groups. <b>Left:</b> the distances within a group and between the two groups. <b>Right:</b> the share of points whose nearest neighbour belongs to their own group, as noise features are added.</div>
    <div class="r2">
      <LineChart :series="[hist(now.win, BLUE), hist(now.btw, GOLD)]" :x-domain="[0, E[E.length - 1]]" :y-domain="[0, ymax]"
        :y-ticks="[]" x-label="distance within a group (blue) / between the groups (gold)"
        :title="`2 useful features + ${m} useless ones`" />
      <LineChart :series="[{ points: curve, color: GREEN, width: 2.2 }]" :dots="[{ x: m, y: pNow, color: GREEN, r: 5 }]"
        :x-domain="[0, 300]" :y-domain="[0.4, 1.02]" :x-ticks="[0, 100, 200, 300]" :y-ticks="[0.5, 0.75, 1]"
        :hlines="[{ y: 0.5, color: '#cccfd2', dash: '4 4' }]"
        x-label="useless features" y-label="nearest neighbour in the same group" title="are the neighbours still right?" />
    </div>
    <div class="foot">With {{ m }} useless features, <b>{{ (100 * pNow).toFixed(0) }}%</b> of the points still have their nearest neighbour in their own group:
      the noise drowns the two features that matter, and every map inherits the wrong neighbours.</div>
    <div class="controls">
      <Knob v-model="noise" :min="0" :max="300" :step="1" :digits="0" label="useless features" :color="GOLD" />
      <Knob v-model="sd" :min="0.1" :max="2" :step="0.05" label="noise level (std)" :color="BLUE" />
    </div>
  </div>
</template>
