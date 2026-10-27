<!-- elbo_mstep: push the bound up. With q fixed, climb the bound to its top:
     theta^{t+1}. The log-likelihood there is at least the bound's top. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace } from '../lib/gmm'
import { curve } from '../lib/charts'
import { argmaxG, G, L, T_HI, T_LO } from '../lib/toy'
import { BLUE, GREEN, INK } from '../lib/theme'

const tb = ref(-0.5)
const t = linspace(T_LO, T_HI, 400)
const tn = computed(() => argmaxG(tb.value))
</script>

<template>
  <div class="wrap">
    <div class="note top" :style="{ color: GREEN }">Push the bound up: with q fixed, climb the bound</div>
    <div class="body">
      <LineChart
        :series="[
          { points: curve(t, L), color: INK, width: 2.6 },
          { points: curve(t, (v) => G(v, tb)), color: BLUE, width: 1.8, dash: '6 4' },
          { points: [[tb, L(tb)], [tn, G(tn, tb)]], color: GREEN, width: 2.2 },
          { points: [[tn, G(tn, tb)], [tn, L(tn)]], color: INK, width: 1.8 },
        ]"
        :dots="[{ x: tb, y: L(tb), color: BLUE, r: 6 }, { x: tn, y: G(tn, tb), color: GREEN, r: 6 }, { x: tn, y: L(tn), color: INK, r: 6 }]"
        :vlines="[{ x: tb, color: '#cccfd2', dash: '2 3' }, { x: tn, color: '#cccfd2', dash: '2 3' }]"
        :labels="[
          { x: tb, y: -2.4, text: 'θᵗ', color: BLUE, size: 14, anchor: 'middle' },
          { x: tn, y: -2.4, text: 'θᵗ⁺¹', color: GREEN, size: 14, anchor: 'middle' },
          { x: 2.5, y: L(2.5) + 0.12, text: 'ℓ_obs(θ)', color: INK, size: 14 },
        ]"
        :x-domain="[T_LO, T_HI]" :y-domain="[-2.5, 0.6]" x-label="θ" :x-ticks="[]" :y-ticks="[]"
      />
      <div class="side">
        <div class="h" :style="{ color: GREEN }">M-step</div>
        <p>— moves θ, never q</p>
        <p>— θᵗ⁺¹ = argmax<sub>θ</sub> F(θ, q): F is separable, so there is a closed form</p>
        <p class="note" style="margin-top: 0.6rem">E<sub>q</sub>[log q] does not involve θ: maximising F is maximising E<sub>q</sub>[ℓ(θ; x, z)].</p>
        <p>ℓ<sub>obs</sub>: {{ L(tb).toFixed(3) }} → <b :style="{ color: GREEN }">{{ L(tn).toFixed(3) }}</b></p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="tb" :min="-0.8" :max="2.6" :step="0.01" label="θᵗ" :color="BLUE" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
</style>
