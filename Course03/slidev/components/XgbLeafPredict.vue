<!-- xgb_leaf_predict: a row is routed to exactly one leaf per tree, and
     collects eta times that leaf's value. The ledger is a real boosting run. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { treeToy } from '../lib/databis'
import { fitBooster } from '../lib/boost'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const eta = ref(0.3)
const row = ref(4)
const shown = ref(4)
const MAX = 30
const data = treeToy(0, 200)

const model = computed(() =>
  fitBooster(data.X, data.y, {
    nTrees: MAX, eta: eta.value, maxDepth: 2, loss: 'log', seed: 0,
  }),
)
const x = computed(() => data.X[Math.round(row.value)])
const ledger = computed(() => {
  const m = model.value
  const out: { name: string; w: number; step: number; F: number }[] = []
  let F = m.f0
  out.push({ name: 'F₀', w: NaN, step: m.f0, F })
  for (let t = 0; t < Math.round(shown.value); t++) {
    const w = m.trees[t].predict(x.value)[0]
    F += eta.value * w
    out.push({ name: `tree ${t + 1}`, w, step: eta.value * w, F })
  }
  return out
})
const finalF = computed(() => model.value.raw(x.value))
const prob = computed(() => 1 / (1 + Math.exp(-finalF.value)))
const truth = computed(() => data.y[Math.round(row.value)])
const tree1 = computed(() => model.value.trees[0])
</script>

<template>
  <div class="wrap">
    <div class="left">
      <TreeDiagram
        :root="tree1.root" :max-depth="3" :probe="x" leaf-text="value"
        title="tree 1: the splits only decide WHICH leaf"
      />
      <p class="note center">
        the thick path is where this row goes; the leaf value at the end of it is the
        tree's whole contribution for this row
      </p>
    </div>
    <div class="right">
      <table class="plain">
        <thead>
          <tr><th></th><th>leaf it lands in</th><th>η × it</th><th>running F</th></tr>
        </thead>
        <tbody>
          <tr v-for="(r, i) in ledger" :key="i">
            <td :style="{ color: i ? INK : MUTED }">{{ r.name }}</td>
            <td :style="{ color: i ? GREEN : MUTED }">{{ isNaN(r.w) ? 'base score' : `w* = ${r.w.toFixed(2)}` }}</td>
            <td :style="{ color: BLUE }">{{ isNaN(r.w) ? '' : (r.step >= 0 ? '+' : '') + r.step.toFixed(3) }}</td>
            <td><b>{{ r.F.toFixed(3) }}</b></td>
          </tr>
          <tr v-if="shown < MAX"><td colspan="4" class="dots">⋮ {{ MAX }} trees in total</td></tr>
        </tbody>
      </table>
      <div class="knobs">
        <Knob v-model="row" :min="0" :max="199" :step="1" label="which row" :digits="0" />
        <Knob v-model="shown" :min="0" :max="10" :step="1" label="trees shown" :digits="0" :color="GREEN" />
        <Knob v-model="eta" :min="0.05" :max="1" label="η" :digits="2" :color="BLUE" />
      </div>
      <Readout
        :items="[
          { label: 'F after all 30', value: finalF.toFixed(3) },
          { label: 'σ(F)', value: prob.toFixed(3), color: prob > 0.5 ? RED : BLUE },
          { label: 'predicted / true', value: `${prob > 0.5 ? 1 : 0} / ${truth}`, color: (prob > 0.5 ? 1 : 0) === truth ? GREEN : RED },
        ]"
      />
      <p class="note">
        F<sub>M</sub>(x) = F₀ + η Σ<sub>m</sub> w*<sub>leaf(x)</sub>; for classification
        the sigmoid is applied once, at the very end.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.left { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; min-height: 0; }
.right { display: flex; flex-direction: column; justify-content: center; gap: 0.6rem; }
.knobs { display: flex; flex-direction: column; gap: 0.3rem; }
.dots { color: var(--muted); text-align: center; }
td { font-variant-numeric: tabular-nums; }
.note { font-size: 0.78rem; color: var(--muted); margin: 0; line-height: 1.5; }
.center { text-align: center; }
</style>
