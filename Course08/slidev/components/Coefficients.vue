<!-- coefficients_blow_up: the least-squares coefficients for four orders. At
     M = 9 on ten points they are enormous and alternate in sign; more points
     or a ridge penalty hold them down. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { polyFit, sci, sinData } from '../lib/c08'
import { INK, MUTED, RED } from '../lib/theme'

const N = ref(10)
const lam = ref(1e-12)
const seed = ref(0)
const ORDERS = [0, 1, 3, 9]
const fits = computed(() => {
  const s = sinData(N.value, seed.value)
  return ORDERS.map((m) => polyFit(s.x, s.t, m, lam.value > 1.01e-12 ? lam.value : 0))
})
const fmt = (v: number) => {
  const a = Math.abs(v)
  return (v < 0 ? '−' : '') + (a >= 1000 ? Math.round(a).toLocaleString('en-US') : a.toFixed(1))
}
const big = (v: number) => Math.abs(v) >= 50
</script>

<template>
  <div class="wrap">
    <table class="coef">
      <tbody>
      <tr><th></th><th v-for="m in ORDERS" :key="m"><Tex :formula="`M = ${m}`" /></th></tr>
      <tr v-for="j in 10" :key="j">
        <td class="lab"><Tex :formula="`w_${j - 1}`" /></td>
        <td v-for="(w, c) in fits" :key="c" :style="{ color: j - 1 < w.length ? (big(w[j - 1]) ? RED : INK) : MUTED, fontWeight: j - 1 < w.length && big(w[j - 1]) ? 700 : 400 }">
          {{ j - 1 < w.length ? fmt(w[j - 1]) : '—' }}
        </td>
      </tr>
    </tbody>
    </table>
    <div class="note msg">
      With ten points the M = 9 coefficients are huge and alternate in sign: huge terms cancelling to pass through every point.
      More points, or a small λ, keep them tame.
    </div>
    <div class="controls">
      <Knob v-model="N" :min="10" :max="200" :step="1" :digits="0" label="points N" />
      <Knob v-model="lam" :min="1e-12" :max="1" log label="ridge λ" />
      <Knob v-model="seed" :min="0" :max="30" :step="1" :digits="0" label="sample" />
      <span class="note">{{ lam > 1.01e-12 ? `λ = ${sci(lam)}` : 'λ = 0' }}</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.coef { width: 86%; margin: 0 auto; font-size: 0.82rem; font-variant-numeric: tabular-nums; }
.coef th { text-align: center; color: #1b1b1b; }
.coef td { text-align: center; padding: 0.12rem 0.5rem; border-bottom: none; }
.coef td.lab { color: #9aa0a6; text-align: left; width: 8%; }
.msg { text-align: center; }
</style>
