<!-- canonical: (w, b) and (sw, sb) are the same boundary. Scaling only moves
     the f = ±1 lines, so we are free to fix the scale by demanding
     min_i |f(x_i)| = 1, and then the margin is exactly 2/||w||. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sepBlobs, toPm1 } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { GREEN, INK, MUTED } from '../lib/theme'

const data = sepBlobs(90, 2.6, 3)
const model = fitSvc(data.X, toPm1(data.y), 1000, kernel({ type: 'linear' }))
const w0 = model.w as number[]
const b0 = model.b

const s = ref(1)
const w = computed(() => [w0[0] * s.value, w0[1] * s.value])
const b = computed(() => b0 * s.value)

/** smallest |f| over the training set, under the current scaling */
const minAbsF = computed(() => {
  let m = Infinity
  for (const [x1, x2] of data.X)
    m = Math.min(m, Math.abs(w.value[0] * x1 + w.value[1] * x2 - b.value))
  return m
})
const norm = computed(() => Math.hypot(w.value[0], w.value[1]))
const canonical = computed(() => Math.abs(minAbsF.value - 1) < 0.02)

const boundary = computed(() => ({ a: -w0[0] / w0[1], c: b0 / w0[1] }))
/** the lines where f = ±1 for the current (w, b) */
const levelLines = computed(() => {
  const [w1, w2] = w.value
  return [-1, 1].map((lv) => ({
    a: -w1 / w2,
    c: (b.value + lv) / w2,
    color: canonical.value ? GREEN : MUTED,
    width: 1.4,
    dash: [6, 5] as number[],
  }))
})
const lines = computed(() => [
  { a: boundary.value.a, c: boundary.value.c, color: INK, width: 2.2 },
  ...levelLines.value,
])
const rings = computed(() =>
  canonical.value ? [{ idx: model.sv, color: GREEN, size: 120, width: 1.8 }] : [],
)
</script>

<template>
  <div class="wrap">
    <FieldPlot :X="data.X" :y="data.y" :lines="lines" :rings="rings" :point-size="18" />
    <div class="side">
      <Knob v-model="s" :min="0.25" :max="4" :step="0.01" label="scale the weights by s" :digits="2" :color="INK" />
      <table>
        <tr>
          <td class="lab">weights</td>
          <td class="val">(s·w, s·b)</td>
        </tr>
        <tr>
          <td class="lab">boundary</td>
          <td class="val" :style="{ color: GREEN }">unchanged</td>
        </tr>
        <tr>
          <td class="lab">min<sub>i</sub> |f(x<sub>i</sub>)|</td>
          <td class="val" :style="{ color: canonical ? GREEN : INK }">{{ minAbsF.toFixed(2) }}</td>
        </tr>
        <tr>
          <td class="lab">‖w‖</td>
          <td class="val">{{ norm.toFixed(2) }}</td>
        </tr>
        <tr>
          <td class="lab">2/‖w‖</td>
          <td class="val" :style="{ color: canonical ? GREEN : MUTED }">{{ (2 / norm).toFixed(2) }}</td>
        </tr>
      </table>
      <p v-if="canonical" class="note green">
        canonical choice: the support vectors sit exactly on f = ±1, and the margin
        is 2/‖w‖ = {{ (2 / norm).toFixed(2) }}
      </p>
      <p v-else class="note">
        the same line, the same data; only the <em>values</em> of f changed.
        The dashed f = ±1 lines moved, so 2/‖w‖ is not yet the margin.
        <button @click="s = 1 / minAbsF * s">fix the scale</button>
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.6rem; }
table { font-size: 0.84rem; border-collapse: collapse; }
td { padding: 0.1rem 0.6rem 0.1rem 0; }
.lab { color: v-bind(MUTED); }
.val { font-variant-numeric: tabular-nums; font-weight: 600; }
.note { font-size: 0.78rem; color: v-bind(MUTED); margin: 0; line-height: 1.45; }
.note.green { color: v-bind(GREEN); }
button {
  border: 1px solid #d8dadd; background: white; border-radius: 0.3rem;
  padding: 0.1rem 0.45rem; font-size: 0.74rem; cursor: pointer; margin-left: 0.2rem;
}
button:hover { border-color: v-bind(GREEN); color: v-bind(GREEN); }
</style>
