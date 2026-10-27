<!-- gmm_params: how many numbers a Gaussian mixture costs, for the K and d
     of your choice. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GOLD, GREEN, INK, PURPLE } from '../lib/theme'

const K = ref(3)
const d = ref(2)
const rows = computed(() => {
  const k = K.value, dd = d.value
  return [
    { name: 'weights', color: PURPLE, sym: 'p₁, …, p_K', count: 'K − 1', v: k - 1, why: 'one is fixed by the others' },
    { name: 'centres', color: BLUE, sym: 'μ₁, …, μ_K', count: 'K d', v: k * dd, why: 'one vector per component' },
    { name: 'spread, spherical', color: GREEN, sym: 'σₖ² I', count: 'K', v: k, why: 'one width per component' },
    { name: 'spread, diagonal', color: GREEN, sym: 'diag(Σₖ)', count: 'K d', v: k * dd, why: 'one width per axis, per component' },
    { name: 'spread, full', color: GOLD, sym: 'Σₖ', count: 'K d(d+1)/2', v: (k * dd * (dd + 1)) / 2, why: 'every covariance' },
  ]
})
const total = computed(() => (K.value * (d.value + 1) * (d.value + 2)) / 2 - 1)
</script>

<template>
  <div class="wrap">
    <div class="note top">How many numbers a Gaussian mixture costs</div>
    <table class="plain big">
      <tr><th>Piece</th><th>Symbol</th><th>Count</th><th>here</th><th>Why</th></tr>
      <tr v-for="r in rows" :key="r.name">
        <td :style="{ color: r.color, fontWeight: 700 }">{{ r.name }}</td>
        <td>{{ r.sym }}</td><td>{{ r.count }}</td>
        <td style="font-weight: 600; text-align: right">{{ r.v }}</td>
        <td class="note">{{ r.why }}</td>
      </tr>
    </table>
    <div class="boxes">
      <div class="box" style="border-color: #1b1b1b">In 1-D: 3K − 1 = <b>{{ 3 * K - 1 }}</b></div>
      <div class="box gold">In d-D, full: K(d+1)(d+2)/2 − 1 = <b>{{ total }}</b></div>
    </div>
    <div class="controls">
      <Knob v-model="K" :min="1" :max="10" :step="1" label="components K" :digits="0" :color="INK" />
      <Knob v-model="d" :min="1" :max="50" :step="1" label="dimension d" :digits="0" :color="GOLD" />
      <span class="note">full covariances grow like K d²</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto auto 1fr auto; gap: 0.6rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.big { font-size: 0.95rem; }
.big td { padding: 0.45rem 1rem 0.45rem 0; }
.boxes { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; align-self: center; }
</style>
