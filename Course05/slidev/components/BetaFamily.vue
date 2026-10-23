<!-- eq_beta_divergence: one formula for the three losses. Slide beta
     continuously from Itakura-Saito through KL to the square, and past. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { dBeta, range } from '../lib/losses'
import { BLUE, GOLD, GREEN, INK, PURPLE } from '../lib/theme'

const beta = ref(1.5)
const x = ref(1)
const ys = range(0.02, 3, 200)
const refs = [{ b: 2, color: BLUE }, { b: 1, color: GREEN }, { b: 0, color: GOLD }]
const curve = computed(() => ys.map((y) => [y, dBeta(x.value, y, beta.value)] as [number, number]))
const named = computed(() => {
  const b = beta.value
  if (Math.abs(b - 2) < 0.03) return 'quadratic'
  if (Math.abs(b - 1) < 0.03) return 'KL'
  if (Math.abs(b) < 0.03) return 'Itakura–Saito'
  return `β = ${b.toFixed(2)}`
})
</script>

<template>
  <div class="wrap">
    <div class="left">
      <div class="note">The three are one family</div>
      <Tex formula="d_\beta(x, y) = \frac{1}{\beta(\beta - 1)} \left( x^\beta + (\beta - 1)\, y^\beta - \beta\, x\, y^{\beta - 1} \right)" display />
      <table class="plain fam">
        <tbody>
          <tr><td :style="{ color: BLUE }">β = 2</td><td :style="{ color: BLUE }"><b>quadratic</b></td><td class="note">Gaussian</td></tr>
          <tr><td :style="{ color: GREEN }">β = 1</td><td :style="{ color: GREEN }"><b>KL</b></td><td class="note">Poisson</td></tr>
          <tr><td :style="{ color: GOLD }">β = 0</td><td :style="{ color: GOLD }"><b>Itakura–Saito</b></td><td class="note">multiplicative</td></tr>
        </tbody>
      </table>
      <p class="note">β = 1 and β = 0 are limits: the formula is 0/0 there, and L'Hôpital gives back KL and Itakura–Saito.</p>
      <p class="note">d<sub>β</sub>(λx, λy) = λ<sup>β</sup> d<sub>β</sub>(x, y): only β = 0 is scale invariant. Here scaling the data by 2 multiplies the loss by <b :style="{ color: PURPLE }">{{ (2 ** beta).toFixed(2) }}</b>.</p>
    </div>
    <div class="right">
      <LineChart
        :series="[...refs.map((r) => ({ points: ys.map((y) => [y, dBeta(x, y, r.b)]), color: r.color, width: 1.4, opacity: 0.35 })), { points: curve, color: PURPLE, width: 3 }]"
        :vlines="[{ x, color: '#9aa0a6', dash: '4 3' }]"
        :x-domain="[0, 3]" :y-domain="[0, 2]" :x-label="`y, for x = ${x.toFixed(2)}`" :x-ticks="[0, 0.5, 1, 1.5, 2, 2.5, 3]" :y-ticks="[0, 0.5, 1, 1.5, 2]"
        :title="named" :title-color="PURPLE"
      />
      <div class="controls">
        <Knob v-model="beta" :min="-1" :max="3" :step="0.01" label="β" :color="PURPLE" />
        <Knob v-model="x" :min="0.3" :max="2" :step="0.05" label="data x" :color="INK" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 2rem; height: 100%; min-height: 0; }
.left { display: flex; flex-direction: column; justify-content: center; gap: 0.4rem; font-size: 0.9rem; }
.fam { width: auto; font-size: 0.95rem; }
.fam td { padding: 0.3rem 1.4rem 0.3rem 0; border: none; }
.right { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; min-height: 0; }
</style>
