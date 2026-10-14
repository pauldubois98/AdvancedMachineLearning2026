<!-- eq_huygens: moving the reference point costs exactly n ||m_a - m||^2.
     Drag the red reference around (click the panel) and both sides of the
     identity are recomputed. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const m = ref<[number, number]>([2.1, 1.0])
const X = (() => {
  const rng = new Rng(14)
  return Array.from({ length: 26 }, () => [rng.normal(0, 0.55), rng.normal(0, 0.55)])
})()
const ma = [
  X.reduce((s, p) => s + p[0], 0) / X.length,
  X.reduce((s, p) => s + p[1], 0) / X.length,
]
const inner = X.reduce((s, p) => s + (p[0] - ma[0]) ** 2 + (p[1] - ma[1]) ** 2, 0)
const toM = computed(() => X.reduce((s, p) => s + (p[0] - m.value[0]) ** 2 + (p[1] - m.value[1]) ** 2, 0))
const shift = computed(() => X.length * ((ma[0] - m.value[0]) ** 2 + (ma[1] - m.value[1]) ** 2))
const gap = computed(() => toM.value - (inner + shift.value))
const far = X.reduce((a, p) =>
  (p[0] - ma[0]) ** 2 + (p[1] - ma[1]) ** 2 > (a[0] - ma[0]) ** 2 + (a[1] - ma[1]) ** 2 ? p : a, X[0])
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :point-size="3.4" :colors="X.map(() => BLUE)" :domain="[-2.4, 3.6, -2.2, 2.4]"
      :spokes="X.map((p) => ({ from: p as [number, number], to: m, color: RED, alpha: 0.25 }))"
      :edges="[
        { a: far as [number, number], b: ma as [number, number], color: BLUE, width: 1.8 },
        { a: ma as [number, number], b: m, color: GREEN, width: 1.8 },
      ]"
      :crosses="[{ x: ma[0], y: ma[1], color: BLUE }, { x: m[0], y: m[1], color: RED }]"
      :tags="[
        { x: ma[0] - 0.1, y: ma[1] - 0.32, text: 'm_a', color: BLUE, size: 12 },
        { x: m[0] + 0.3, y: m[1], text: 'm', color: RED, size: 12 },
      ]"
      title="click anywhere to move the reference point m" :title-color="RED"
      @pick="(p) => (m = p)"
    />
    <div class="right">
      <div class="formula">
        <Tex display formula='\sum_{x \in C_a} \|x - m\|^2 = \sum_{x \in C_a} \|x - m_a\|^2 + n_a \|m_a - m\|^2' />
      </div>
      <table class="plain">
        <tr>
          <td>Σ ‖x − m‖², measured</td>
          <td :style="{ color: RED, fontWeight: 600 }">{{ toM.toFixed(3) }}</td>
        </tr>
        <tr>
          <td>Σ ‖x − m<sub>a</sub>‖², the inertia</td>
          <td :style="{ color: BLUE, fontWeight: 600 }">{{ inner.toFixed(3) }}</td>
        </tr>
        <tr>
          <td>n<sub>a</sub> ‖m<sub>a</sub> − m‖², the shift</td>
          <td :style="{ color: GREEN, fontWeight: 600 }">{{ shift.toFixed(3) }}</td>
        </tr>
        <tr>
          <td>difference between the two sides</td>
          <td :style="{ color: Math.abs(gap) < 1e-9 ? GREEN : RED, fontWeight: 600 }">{{ gap.toExponential(1) }}</td>
        </tr>
      </table>
      <p class="note">because x − m = (x − m<sub>a</sub>) + (m<sub>a</sub> − m),
        and the cross term 2 (m<sub>a</sub> − m) · Σ (x − m<sub>a</sub>) vanishes:
        <em class="hl-green">Σ (x − m<sub>a</sub>) = 0</em> is the definition of
        a centroid.</p>
      <p class="note">So the inertia of a group is the smallest it can be about
        its own centroid, and moving the reference costs exactly the shift term.
        That is the whole of Ward's formula.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.05fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.6rem; justify-content: center; }
.formula { font-size: 0.8rem; }
</style>
