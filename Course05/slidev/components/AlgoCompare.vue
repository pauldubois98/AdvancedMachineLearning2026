<!-- algo_compare: MU, ALS and HALS from the same NNDSVD start, run live on the
     same faces, per pass and per second of work. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { faces } from '../lib/data5'
import { clone } from '../lib/mat'
import { type Algo, type Fit, init, lossOf, step } from '../lib/nmf'
import { useRun } from '../lib/runner'
import { BLUE, GOLD, INK, PURPLE } from '../lib/theme'
import { logTicks, niceTicks } from '../lib/ticks'

const X = faces(150)
const r = ref(12)
const PASSES = 120
const el = ref<HTMLElement | null>(null)
let start: Fit | null = null
let startR = -1
const startFor = (k: number) => { if (startR !== k) { start = init(X, k, 'nndsvd'); startR = k } return start! }
const algos: { name: string; algo: Algo; color: string }[] = [
  { name: 'MU', algo: 'mu', color: BLUE },
  { name: 'ALS', algo: 'als', color: PURPLE },
  { name: 'HALS', algo: 'hals', color: GOLD },
]
const runs = algos.map((a) => {
  const secs: number[] = [0]
  const run = useRun<Fit & { t: number }>({
    el, key: () => r.value,
    make: () => { const s = startFor(r.value); secs.length = 1; return { W: clone(s.W), H: clone(s.H), t: 0 } },
    step: (f) => { const t0 = performance.now(); step(a.algo, X, f); f.t += (performance.now() - t0) / 1000; secs.push(f.t) },
    score: (f) => lossOf(X, f),
    passes: () => PASSES,
  })
  return { ...a, run, secs }
})
const rises = (h: [number, number][]) => h.slice(1).filter((p, i) => p[1] > h[i][1] * (1 + 1e-9)).length
const ydom = computed(() => {
  const ys = runs.flatMap((x) => x.run.hist.value.map((p) => p[1]))
  return ys.length ? [Math.min(...ys) * 0.95, Math.max(...ys) * 1.05] as [number, number] : [1, 10] as [number, number]
})
const tmax = computed(() => { void runs[0].run.tick.value; return Math.max(...runs.map((x) => x.secs[x.secs.length - 1]), 1e-3) })
</script>

<template>
  <div ref="el" class="wrap">
    <div class="note top">{{ X.c }} faces, r = {{ r }}, the same NNDSVD start for all three, run live in this browser</div>
    <div class="body">
      <LineChart
        :series="runs.map((x) => ({ points: x.run.hist.value, color: x.color, width: 2.2 }))"
        log-y :x-domain="[0, PASSES]" :y-domain="ydom" :y-ticks="logTicks(...ydom)" x-label="pass" y-label="½‖X − WH‖²" :x-ticks="[0, 25, 50, 75, 100]" title="per pass"
      />
      <LineChart
        :series="runs.map((x) => ({ points: x.run.hist.value.map(([p, v]) => [x.secs[p] ?? 0, v]), color: x.color, width: 2.2 }))"
        log-y :x-domain="[0, tmax]" :y-domain="ydom" :y-ticks="logTicks(...ydom)" :x-ticks="niceTicks(0, tmax, 4)" x-label="seconds" title="per second of work"
      />
      <div class="side">
        <div class="h">after {{ runs[0].run.pass.value }} passes</div>
        <p v-for="x in runs" :key="x.name" :style="{ color: x.color }"><b>{{ x.name }}</b>: {{ (x.run.hist.value.at(-1)?.[1] ?? 0).toFixed(1) }}</p>
        <p class="note">ALS is not monotone: it rose on {{ rises(runs[1].run.hist.value) }} of its {{ Math.max(runs[1].run.hist.value.length - 1, 0) }} steps. MU never rises, but crawls.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="r" :min="2" :max="24" :step="1" label="r" :digits="0" :color="INK" />
    </div>
    <div class="credit">data: Olivetti faces, AT&amp;T Cambridge (shrunk to 32 × 32)</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1fr 12rem; gap: 1.6rem; min-height: 0; }
.side { align-self: center; }
</style>
