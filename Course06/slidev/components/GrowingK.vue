<!-- gmm_flexible: a skewed, heavy-shouldered sample, fitted by EM with K
     components, live. The likelihood only ever rises with K. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { em1, linspace, mixPdf1, skewedSample, start1, weighted1 } from '../lib/gmm'
import { bars, curve, edges, fmt } from '../lib/charts'
import { BLUE, MUTED, INK } from '../lib/theme'

const x = skewedSample(1000, 11)
const K = ref(2)
const grid = linspace(-0.5, 10.5, 400)
const hist = bars(x, edges(-0.5, 10.5, 11 / 60), { density: true })
function fit(k: number) {
  // best of two random starts, as one would in practice
  let best = null as null | ReturnType<typeof em1>[number]
  for (let s = 0; s < 2; s++) {
    const h = em1(x, start1(x, k, 2 + 97 * s), 150)
    const last = h[h.length - 1]
    if (!best || last.ll > best.ll) best = last
  }
  return best!
}
const cache = new Map<number, ReturnType<typeof fit>>()
const fitK = (k: number) => { if (!cache.has(k)) cache.set(k, fit(k)); return cache.get(k)! }
const m = computed(() => fitK(K.value))
const lls = computed(() => [1, 2, 3, 4, 5, 6, 8, 10].map((k) => ({ k, ll: k === K.value || cache.has(k) ? fitK(k).ll : null })))
</script>

<template>
  <div class="wrap">
    <div class="note top">More components always give a better fit.</div>
    <div class="body">
      <LineChart
        :series="[
          ...m.p.map((_, k) => ({ points: curve(grid, (v) => weighted1(v, m)[k]), color: MUTED, width: 1.1, dash: '5 4' })),
          { points: curve(grid, (v) => mixPdf1(v, m)), color: BLUE, width: 2.6 },
        ]"
        :bars="hist" :x-domain="[-0.5, 10.5]" :y-domain="[0, 0.42]" :x-ticks="[0, 2, 4, 6, 8, 10]" :y-ticks="[]"
        :title="`K = ${K}: log-likelihood ${fmt(m.ll)}`" :title-color="BLUE"
      />
      <div class="side">
        <div class="h">Log-likelihood by K</div>
        <table class="plain">
          <tr v-for="r in lls" :key="r.k" :style="{ fontWeight: r.k === K ? 700 : 400, color: r.k === K ? BLUE : INK }">
            <td>K = {{ r.k }}</td><td style="text-align: right">{{ r.ll === null ? '·' : fmt(r.ll) }}</td>
          </tr>
        </table>
        <p class="note" style="margin-top: 0.6rem">Each K is filled in once visited. Choosing K needs another criterion than the likelihood.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="K" :min="1" :max="10" :step="1" label="components K" :digits="0" :color="BLUE" />
      <span class="note">EM, 150 passes, best of two random starts, refitted as K moves.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
