<!-- jensen_picture: a concave function sits above its chords. Two values of
     u and a weight: log of the average against the average of the logs. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { linspace } from '../lib/gmm'
import { curve } from '../lib/charts'
import { GOLD, GREEN, INK, RED } from '../lib/theme'

const u1 = ref(0.6)
const u2 = ref(5.4)
const w = ref(0.55)
const grid = linspace(0.25, 6.2, 300)
const Eu = computed(() => w.value * u1.value + (1 - w.value) * u2.value)
const Elog = computed(() => w.value * Math.log(u1.value) + (1 - w.value) * Math.log(u2.value))
</script>

<template>
  <div class="wrap">
    <div class="note top">A concave function sits above its chords</div>
    <div class="body">
      <LineChart
        :series="[
          { points: curve(grid, Math.log), color: INK, width: 2.6 },
          { points: [[u1, Math.log(u1)], [u2, Math.log(u2)]], color: GOLD, width: 2 },
          { points: [[Eu, Elog], [Eu, Math.log(Eu)]], color: RED, width: 2.4 },
        ]"
        :dots="[
          { x: u1, y: Math.log(u1), color: GOLD, r: 5 }, { x: u2, y: Math.log(u2), color: GOLD, r: 5 },
          { x: Eu, y: Math.log(Eu), color: GREEN, r: 6 }, { x: Eu, y: Elog, color: RED, r: 6 },
        ]"
        :labels="[
          { x: Eu + 0.15, y: Math.log(Eu) + 0.25, text: 'log E[u]', color: GREEN, size: 14 },
          { x: Eu + 0.15, y: Elog - 0.3, text: 'E[log u]', color: RED, size: 14 },
        ]"
        :x-domain="[0, 6.4]" :y-domain="[-1.5, 2.3]" x-label="u" y-label="log u" :x-ticks="[1, 2, 3, 4, 5, 6]" :y-ticks="[-1, 0, 1, 2]"
      />
      <div class="side">
        <div class="h" :style="{ color: GREEN }">log E[u] ≥ E[log u]</div>
        <p>— applied with u(z) = f(x, z | θ) / q(z)</p>
        <p>— the average is over z ∼ q</p>
        <p>— the chord shrinks to a point when u is constant in z</p>
        <p class="big">gap = <b :style="{ color: RED }">{{ (Math.log(Eu) - Elog).toFixed(3) }}</b></p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="u1" :min="0.3" :max="6" :step="0.01" label="u₁" :color="GOLD" />
      <Knob v-model="u2" :min="0.3" :max="6" :step="0.01" label="u₂" :color="GOLD" />
      <Knob v-model="w" :min="0" :max="1" :step="0.01" label="weight q(z₁)" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
.big { font-size: 1.05rem; margin-top: 0.6rem; }
</style>
