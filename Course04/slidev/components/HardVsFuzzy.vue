<!-- hard_vs_fuzzy: a label, or a weight per cluster. The fuzzifier m decides
     how quickly a point stops being shared; click a point to read its weights. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { fuzzyWeights } from '../lib/cluster'
import { BLUE, GREEN, RED, mix } from '../lib/theme'

const m = ref(2)
const pick = ref(0)
const centres = [[-0.95, 0], [0.95, 0]]
const X = (() => {
  const rng = new Rng(13)
  const out: number[][] = []
  for (const c of centres) for (let i = 0; i < 70; i++) out.push([rng.normal(c[0], 0.72), rng.normal(c[1], 0.72)])
  return out
})()
const hard = X.map((p) =>
  Math.hypot(p[0] - centres[0][0], p[1] - centres[0][1]) <=
  Math.hypot(p[0] - centres[1][0], p[1] - centres[1][1]) ? 0 : 1,
)
const W = computed(() => fuzzyWeights(X, centres, m.value))
const colors = computed(() => W.value.map((w) => mix(RED, BLUE, w[0])))
/** how many points are genuinely shared, i.e. neither weight dominates */
const shared = computed(() => W.value.filter((w) => Math.min(w[0], w[1]) > 0.35).length)
const dom: [number, number, number, number] = [-3.2, 3.2, -2.3, 2.5]

function onPick(p: [number, number]) {
  let best = 0
  let bd = Infinity
  X.forEach((q, i) => {
    const d = (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2
    if (d < bd) { bd = d; best = i }
  })
  pick.value = best
}
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <ClusterPlot
        :X="X" :labels="hard" :domain="dom" :point-size="3"
        title="hard: a single label" :title-color="BLUE"
      />
      <ClusterPlot
        :X="X" :colors="colors" :domain="dom" :point-size="3"
        :circles="[{ x: X[pick][0], y: X[pick][1], r: 0.16, color: '#1b1b1b', alpha: 0 }]"
        :tags="[{ x: X[pick][0], y: X[pick][1] + 0.42, text: `w₁ = ${W[pick][0].toFixed(2)}, w₂ = ${W[pick][1].toFixed(2)}`, size: 12 }]"
        title="fuzzy: a weight per cluster (click a point)" :title-color="GREEN" @pick="onPick"
      />
      <div class="side">
        <p><em class="hl-blue">hard</em><br /><span class="note">x<sub>i</sub> gets one label</span></p>
        <p><em class="hl-green">fuzzy</em><br />
          <span class="note">x<sub>i</sub> gets a weight w<sub>k</sub> ∈ [0, 1] for every cluster,
          with Σ<sub>k</sub> w<sub>k</sub> = 1</span></p>
        <p class="note">m → 1 makes the weights nearly hard; large m makes
          everything belong to everything.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="m" :min="1.1" :max="5" label="fuzzifier m" :color="GREEN" />
      <Readout
        :items="[
          { label: 'genuinely shared points', value: String(shared), color: GREEN },
          { label: 'weights of the marked point', value: `${W[pick][0].toFixed(2)} / ${W[pick][1].toFixed(2)}` },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr 0.86fr; gap: 1rem; min-height: 0; }
.side { font-size: 0.85rem; align-self: center; }
.side p { margin: 0 0 0.7rem; line-height: 1.5; }
.controls { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 13rem; }
</style>
