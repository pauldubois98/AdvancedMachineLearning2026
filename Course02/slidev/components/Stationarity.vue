<!-- eq_stationarity: why ρ̇ appears. The slope of ρ at a residual is how hard
     that point pulls on the fit; least squares lets the pull grow without bound. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { curve } from '../lib/hist'
import { psiHuber, rhoHuber } from '../lib/reg'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const e = ref(3.4)
const d = ref(1.5)
const tan = (f: (v: number) => number, s: number, color: string) => ({ points: [[e.value - 1.4, f(e.value) - 1.4 * s], [e.value + 1.4, f(e.value) + 1.4 * s]] as [number, number][], color, width: 2 })
const hub = (v: number) => rhoHuber(v, d.value)
const sl = computed(() => psiHuber(e.value, d.value))
const col = computed(() => (Math.abs(e.value) <= d.value ? GREEN : RED))
</script>

<template>
  <div class="stat">
    <div class="col">
      <LineChart :series="[{ points: curve((v) => 0.5 * v * v, -5, 5), color: MUTED, dash: '6,4', width: 1.6 }, { points: curve(hub, -5, 5), color: INK, width: 2.6 }, tan(hub, sl, col), tan((v) => 0.5 * v * v, e, BLUE)]"
        :dots="[{ x: e, y: hub(e), color: col, r: 6 }, { x: e, y: 0.5 * e * e, color: BLUE, r: 5 }]"
        :x-domain="[-5, 5]" :y-domain="[-0.3, 7]" :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[]" x-label="residual e" y-label="ρ(e)" />
      <div class="note">Huber (black): slope <b :style="{ color: col }">ρ̇(e) = {{ sl.toFixed(2) }}</b>; least squares (dashed): slope <b :style="{ color: BLUE }">{{ e.toFixed(2) }}</b></div>
      <div class="controls">
        <Knob v-model="e" :min="-5" :max="5" :step="0.01" label="residual e" :color="col" />
        <Knob v-model="d" :min="0.2" :max="4" :step="0.01" label="δ" :color="INK" />
      </div>
    </div>
    <div class="side eqs">
      <p class="note"><Tex formula="\dot\rho(e) = \mathrm{d}\rho/\mathrm{d}e" /></p>
      <p>Set gradient to zero:</p>
      <p :style="{ color: GREEN }"><Tex display formula="\frac{\partial}{\partial \beta}\sum_i \rho(y_i - x_i'^{T}\beta) \;=\; -\sum_i \dot\rho(e_i)\, x_i'" /></p>
      <p class="note" style="margin-top: 1rem">least squares:</p>
      <p :style="{ color: BLUE }"><Tex display formula="\rho(e) = \tfrac{e^2}{2} \;\Rightarrow\; \dot\rho(e) = e \;\Rightarrow\; \text{set } \textstyle\sum_i e_i\, x_i' = 0" /></p>
    </div>
  </div>
</template>

<style scoped>
.stat { display: grid; grid-template-columns: 1fr 1.15fr; gap: 1.5rem; height: 100%; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto auto; gap: 0.4rem; min-height: 0; text-align: center; }
.eqs { align-self: center; font-size: 1rem; }
</style>
