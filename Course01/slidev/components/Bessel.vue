<!-- bessel: the sample mean sits where the sample fits best, so the scatter
     around x̄ is smaller than the scatter around the true μ. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve } from '../lib/hist'
import { mean } from '../lib/stats'
import type { Pt } from '../lib/geom'
import { BLUE, GRID, INK, MUTED, RED } from '../lib/theme'

const a = ref(0)
const seed = ref(3)
const N = 8
const x = computed(() => { const r = new Rng(seed.value); return Array.from({ length: N }, () => r.normal(0, 1)) })
const xb = computed(() => mean(x.value))
const ss = (c: number) => x.value.reduce((s, v) => s + (v - c) ** 2, 0)
const S = computed(() => ss(xb.value))
const pts = computed<Pt[]>(() => x.value.map((v) => [v, 0]))
const segs = computed(() => x.value.map((v, i) => ({ a: [v, 0.12 + 0.11 * i] as Pt, b: [a.value, 0.12 + 0.11 * i] as Pt, color: BLUE, width: 2 })))
const segsMu = computed(() => x.value.map((v, i) => ({ a: [v, -0.12 - 0.11 * i] as Pt, b: [0, -0.12 - 0.11 * i] as Pt, color: GRID, width: 2 })))
const sc = computed(() => curve(ss, -2.5, 2.5))
const top = computed(() => Math.max(...sc.value.map((p) => p[1])))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> n = 8 points from N(μ = 0, 1). Above the line, each point's distance to a reference c (the slider); below, its distance to the true μ = 0. Right, Σ (xᵢ − c)² as a function of c.</div>
    <div class="r2">
      <Plane :X="pts" :colors="INK" :size="4.5" :segments="[...segs, ...segsMu, { a: [a, -1.1], b: [a, 1.1], color: BLUE, width: 1.6 }, { a: [0, -1.1], b: [0, 1.1], color: MUTED, width: 1.2 }]"
        :domain="[-2.6, 2.6, -1.1, 1.1]" :equal="false" title="distances to c (blue) and to μ (grey)" />
      <LineChart :series="[{ points: sc, color: BLUE }]" :x-domain="[-2.5, 2.5]" :y-domain="[0, top]" :x-ticks="[-2, -1, 0, 1, 2]" :y-ticks="[]" x-label="the reference c"
        :vlines="[{ x: xb, color: RED, dash: '5,3' }, { x: 0, color: MUTED, dash: '2,3' }]" :dots="[{ x: a, y: ss(a), color: BLUE, r: 6 }, { x: xb, y: S, color: RED, r: 5 }, { x: 0, y: ss(0), color: MUTED, r: 5 }]"
        :labels="[{ x: xb + 0.08, y: top * 0.92, text: 'x̄', color: RED }, { x: 0.08, y: top * 0.82, text: 'μ', color: MUTED }]" title="Σ (xᵢ − c)² = S + n (x̄ − c)²" />
    </div>
    <div class="foot">Σ (xᵢ − c)² = <b :style="{ color: BLUE }">{{ ss(a).toFixed(1) }}</b> · smallest at c = x̄: S = <b :style="{ color: RED }">{{ S.toFixed(1) }}</b> &lt; Σ (xᵢ − μ)² = {{ ss(0).toFixed(1) }}. On average E[S] = (n − 1) σ²: one degree of freedom was spent estimating the mean.</div>
    <div class="controls">
      <Knob v-model="a" :min="-2.4" :max="2.4" :step="0.01" label="reference c" :color="BLUE" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="new sample" :color="INK" />
    </div>
  </div>
</template>
