<!-- eq_aicc: the extra term of the corrected AIC, M(M+1)/(N - M - 1), for a
     chosen number of parameters: large when N/M is small, vanishing as N
     grows, infinite as M approaches N - 1. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GREEN, INK, PURPLE, RED } from '../lib/theme'

const Mj = ref(8)
const N = ref(50)
const extra = (m: number, n: number) => (n - m - 1 > 0 ? (m * (m + 1)) / (n - m - 1) : Infinity)
const cur = computed(() => extra(Mj.value, N.value))
const NS = [20, 50, 100, 500]
const curve = computed(() => {
  const out: [number, number][] = []
  for (let n = Mj.value + 2; n <= 1000; n = Math.ceil(n * 1.04)) out.push([n, Math.min(extra(Mj.value, n), 100)])
  return out
})
const ratio = computed(() => N.value / Mj.value)
</script>

<template>
  <div class="wrap">
    <div class="row">
      <table class="plain ex">
        <tbody>
        <tr><th>extra term at <Tex :formula="`M_j = ${Mj}`" /></th><th v-for="n in NS" :key="n"><Tex :formula="`N = ${n}`" /></th></tr>
        <tr><td></td><td v-for="n in NS" :key="n" :style="{ color: PURPLE, fontWeight: 600 }">{{ Number.isFinite(extra(Mj, n)) ? extra(Mj, n).toFixed(2) : '∞' }}</td></tr>
      </tbody>
      </table>
    </div>
    <div class="body">
      <LineChart
        :series="[{ points: curve, color: PURPLE, width: 2.6 }]"
        :dots="Number.isFinite(cur) ? [{ x: N, y: Math.min(cur, 100), color: PURPLE, r: 6 }] : []"
        :vlines="[{ x: 40 * Mj, color: GREEN, dash: '4 3' }]"
        :labels="[{ x: 40 * Mj * 1.06, y: 60, text: 'N = 40 Mⱼ', color: GREEN, size: 12 }]"
        log-x log-y :x-domain="[10, 1000]" :y-domain="[0.01, 100]" :x-ticks="[10, 100, 1000]" :y-ticks="[0.01, 0.1, 1, 10, 100]"
        x-label="N" y-label="extra penalty" :unit-height="190"
      />
      <div class="side">
        <p>At <Tex formula="M_j" /> = {{ Mj }} and <Tex formula="N" /> = {{ N }}: extra
          <b :style="{ color: PURPLE }">{{ Number.isFinite(cur) ? cur.toFixed(2) : '∞' }}</b>, against the {{ Mj }} of plain AIC.</p>
        <p :style="{ color: ratio < 40 ? RED : GREEN }"><Tex formula="N / M_j" /> = {{ ratio.toFixed(1) }}:
          {{ ratio < 40 ? 'below about 40, use the corrected form' : 'plain AIC is fine' }}</p>
        <p class="note">The term blows up as <Tex formula="M_j \to N - 1" /> and vanishes as <Tex formula="N" /> grows.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="Mj" :min="1" :max="30" :step="1" :digits="0" label="parameters Mⱼ" :color="PURPLE" />
      <Knob v-model="N" :min="3" :max="1000" :step="1" :digits="0" label="points N" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.ex { width: 90%; margin: 0 auto; font-size: 0.9rem; }
.ex td, .ex th { text-align: center; }
.ex th:first-child { text-align: left; }
.body { display: grid; grid-template-columns: 1.2fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; font-size: 0.92rem; }
</style>
