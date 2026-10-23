<!-- loss_axioms: what we ask of d, and what we do not. Move the data x and
     the model y, and read d(x, y) against d(y, x): only the square is
     symmetric. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { dIS, dKL, dQuad } from '../lib/losses'
import { BLUE, GOLD, GREEN, INK, RED } from '../lib/theme'

const x = ref(1)
const y = ref(3)
const rows = computed(() => [
  { name: 'quadratic', color: BLUE, f: dQuad },
  { name: 'KL', color: GREEN, f: dKL },
  { name: 'Itakura–Saito', color: GOLD, f: dIS },
].map((l) => ({ ...l, a: l.f(x.value, y.value), b: l.f(y.value, x.value) })))
</script>

<template>
  <div class="wrap">
    <div class="note top">Requirements for d</div>
    <div class="boxes">
      <div class="card" :style="{ borderColor: GREEN }">
        <div class="h" :style="{ color: GREEN }">ask</div>
        <Tex formula="d(x, x) = 0 \quad \forall x" display />
        <Tex formula="d(x, y) \geq 0 \quad \forall (x, y)" display />
      </div>
      <div class="card" :style="{ borderColor: RED }">
        <div class="h" :style="{ color: RED }">do not ask</div>
        <Tex formula="d(x, y) = d(y, x)" display />
        <Tex formula="d(x, z) \leq d(x, y) + d(y, z)" display />
      </div>
    </div>
    <div class="mid">A divergence, not a distance</div>
    <table class="plain tab">
      <thead><tr><th></th><th>d(x, y): data x, model y</th><th>d(y, x): the arguments swapped</th></tr></thead>
      <tbody>
        <tr v-for="l in rows" :key="l.name">
          <td :style="{ color: l.color }">{{ l.name }}</td>
          <td class="num">{{ l.a.toFixed(2) }}</td>
          <td class="num" :style="{ color: Math.abs(l.a - l.b) > 5e-3 ? RED : INK }">{{ l.b.toFixed(2) }}</td>
        </tr>
      </tbody>
    </table>
    <div class="controls">
      <Knob v-model="x" :min="0.1" :max="4" :step="0.05" label="data x" :color="BLUE" />
      <Knob v-model="y" :min="0.1" :max="4" :step="0.05" label="model y" :color="INK" />
    </div>
    <div class="note bottom">Underestimating and overestimating an entry do not cost the same. The order of the arguments is always d(data, model).</div>
  </div>
</template>

<style scoped>
.wrap { display: flex; flex-direction: column; gap: 0.5rem; height: 100%; }
.top, .bottom, .mid { text-align: center; }
.mid { font-size: 1rem; }
.boxes { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; padding: 0 2rem; }
.boxes .card { padding: 0.4rem; gap: 0; }
.tab { width: 70%; margin: 0 auto; }
.tab td, .tab th { text-align: center; }
.tab td:first-child { text-align: left; font-weight: 600; }
.num { font-variant-numeric: tabular-nums; }
.controls { justify-content: center; }
</style>
