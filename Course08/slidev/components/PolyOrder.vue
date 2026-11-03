<!-- poly_orders: the order-M polynomial fitted to the ten points, M moving
     from a line to one coefficient per point. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { polyFit, polyPoints, ringDots, rms, sinData, truthPoints } from '../lib/c08'
import { BLUE, GREEN, RED } from '../lib/theme'

const M = ref(3)
const s = sinData(10, 0)
const errs = Array.from({ length: 10 }, (_, m) => rms(polyFit(s.x, s.t, m), s))
const w = computed(() => polyFit(s.x, s.t, M.value))
const state = computed(() =>
  M.value <= 2 ? { c: RED, t: 'too rigid to bend, the fit misses the shape (underfitting)' }
    : M.value <= 5 ? { c: GREEN, t: 'close to the green curve it has never seen' }
      : M.value < 9 ? { c: RED, t: 'starts bending towards individual points' }
        : { c: RED, t: 'ten coefficients for ten points, so it passes through every one' })
</script>

<template>
  <div class="wrap">
    <div class="body">
      <LineChart
        :series="[{ points: truthPoints, color: GREEN, width: 2.4 }, { points: polyPoints(w), color: RED, width: 3 }]"
        :dots="ringDots(s, BLUE)" :x-domain="[-0.03, 1.03]" :y-domain="[-1.6, 1.6]" :axes="false"
        :title="`M = ${M}`"
      />
      <div class="side">
        <div class="h">Interpretation</div>
        <p :style="{ color: state.c }">— M = {{ M }}: {{ state.t }}</p>
        <table class="plain">
          <tbody>
          <tr><th>M</th><th v-for="m in 10" :key="m" :style="{ fontWeight: m - 1 === M ? 700 : 400 }">{{ m - 1 }}</th></tr>
          <tr>
            <td style="color: #2b6cb0">train</td>
            <td v-for="(e, m) in errs" :key="m" :style="{ fontWeight: m === M ? 700 : 400, color: m === M ? BLUE : '' }">{{ e.toFixed(2) }}</td>
          </tr>
        </tbody>
        </table>
        <p style="color: #c53030; margin-top: 0.8rem">The best training error belongs to the worst model.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="M" :min="0" :max="9" :step="1" :digits="0" label="order M" :color="state.c" />
      <span class="note">Least squares on the polynomial basis; RMS training error in the table.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1.3fr 1fr; gap: 2.5rem; min-height: 0; }
.side { align-self: center; border-left: 1px solid #cccfd2; padding-left: 2rem; font-size: 0.95rem; }
.side .plain { font-size: 0.72rem; }
.side .plain td, .side .plain th { padding-right: 0.35rem; }
</style>
