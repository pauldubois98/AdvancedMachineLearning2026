<!-- elbo_estep: close the gap. With theta fixed, the E-step lifts the bound
     F(., q) until it touches the log-likelihood at theta^t: the gap is the
     KL divergence between q and the posterior. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace } from '../lib/gmm'
import { curve } from '../lib/charts'
import { G, L, T_HI, T_LO } from '../lib/toy'
import { BLUE, INK, MUTED, RED } from '../lib/theme'

const tb = ref(-0.5)
const lam = ref(0.3)
const t = linspace(T_LO, T_HI, 400)
const drop = computed(() => (1 - lam.value) * 0.9)
</script>

<template>
  <div class="wrap">
    <div class="note top" :style="{ color: BLUE }">Close the gap: with θ fixed, lift the bound until it touches</div>
    <div class="body">
      <LineChart
        :series="[
          { points: curve(t, L), color: INK, width: 2.6 },
          { points: curve(t, (v) => G(v, tb)), color: BLUE, width: 1.8, dash: '6 4', opacity: 0.35 },
          { points: curve(t, (v) => G(v, tb) - drop), color: lam > 0.995 ? BLUE : MUTED, width: 2, dash: lam > 0.995 ? '6 4' : '2 3' },
          { points: [[tb, G(tb, tb) - drop], [tb, L(tb)]], color: RED, width: 2.4 },
        ]"
        :dots="[{ x: tb, y: L(tb), color: BLUE, r: 6 }, { x: tb, y: L(tb) - drop, color: lam > 0.995 ? BLUE : MUTED, r: 4.5 }]"
        :vlines="[{ x: tb, color: '#cccfd2', dash: '2 3' }]"
        :labels="[{ x: 2.5, y: L(2.5) + 0.12, text: 'ℓ_obs(θ)', color: INK, size: 14 }, { x: tb + 0.08, y: L(tb) - drop / 2, text: `KL = ${drop.toFixed(2)}`, color: RED, size: 13 }]"
        :x-domain="[T_LO, T_HI]" :y-domain="[-2.5, 0.6]" x-label="θ" :x-ticks="[]" :y-ticks="[]"
      />
      <div class="side">
        <div class="h" :style="{ color: BLUE }">E-step</div>
        <p>— moves q (not θ)</p>
        <p>— max<sub>q</sub> F(θᵗ, q) is reached at the posterior P(z | x, θᵗ)</p>
        <p>— the KL gap is zero, so F(θᵗ, q) = ℓ<sub>obs</sub>(θᵗ)</p>
        <p class="note" style="margin-top: 0.6rem">In a Gaussian mixture, that posterior is the table γ<sub>ik</sub>. The pale dashed curve is where the bound lands.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="lam" :min="0" :max="1" :step="0.005" label="q: worse → posterior" :digits="2" :color="BLUE" />
      <Knob v-model="tb" :min="-0.8" :max="2.6" :step="0.01" label="θᵗ" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
