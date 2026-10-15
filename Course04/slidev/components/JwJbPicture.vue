<!-- jw_jb_picture: the two sums of the previous slide, drawn. J_w is every
     spoke from a point to its own centre m_i; J_b is every spoke from a centre
     m_i to the centre m of all the data, counted n_i times. The slider moves K,
     and the two trade against each other while their sum stays put. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { blobs } from '../lib/data4'
import { jwJb, kmeans } from '../lib/cluster'
import { BLUE, GREEN, INK, clusterColor } from '../lib/theme'

const k = ref(3)
const data = blobs([[-1.9, -1.0], [1.9, -0.8], [0.0, 1.9]], 0.52, 50, 5)
const dom: [number, number, number, number] = [-4.4, 4.4, -3.2, 3.8]
const m = ((): [number, number] => {
  const n = data.X.length
  return [data.X.reduce((s, p) => s + p[0], 0) / n, data.X.reduce((s, p) => s + p[1], 0) / n]
})()

const run = computed(() => kmeans(data.X, k.value, 0, 8))
const sizes = computed(() => run.value.mu.map((_, c) => run.value.labels.filter((l) => l === c).length))
const score = computed(() => jwJb(data.X, run.value.labels))

const within = computed(() =>
  data.X.map((p, i) => {
    const c = run.value.labels[i]
    return { from: p as [number, number], to: run.value.mu[c] as [number, number], color: clusterColor(c), alpha: 0.55 }
  }),
)
const centres = computed(() =>
  run.value.mu.map((mu, c) => ({ x: mu[0], y: mu[1], color: clusterColor(c), size: 9 })),
)
// a spoke counted n_i times is drawn n_i times as thick
const between = computed(() =>
  run.value.mu.map((mu, c) => ({
    a: mu as [number, number], b: m, color: clusterColor(c), width: 0.6 + sizes.value[c] / 12,
  })),
)
// each label sits beyond its centre, on the far side from m, clear of the
// spokes; past K = 5 they crowd each other, and the widths carry n_i alone
const counts = computed(() => {
  // at K = 1 the only centre is m itself, and J_b has nothing to draw
  if (k.value === 1 || k.value > 5) return []
  return run.value.mu.map((mu, c) => {
    const dx = mu[0] - m[0], dy = mu[1] - m[1]
    const r = Math.hypot(dx, dy) || 1
    const ux = dx / r, uy = dy / r
    return {
      x: mu[0] + 0.5 * ux, y: mu[1] + 0.5 * uy + (uy < -0.3 ? -0.15 : 0),
      text: `n${toSub(c + 1)} = ${sizes.value[c]}`, color: clusterColor(c), size: 12.5,
      anchor: (ux > 0.3 ? 'left' : ux < -0.3 ? 'right' : 'center') as CanvasTextAlign,
    }
  })
})
function toSub(n: number): string {
  return String(n).split('').map((d) => '₀₁₂₃₄₅₆₇₈₉'[Number(d)]).join('')
}
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div class="col">
        <ClusterPlot
          :X="data.X" :labels="run.labels" :domain="dom" :point-size="2.8"
          :spokes="within" :crosses="centres"
          title="J<sub>w</sub>: each point to the centre m<sub>i</sub> of its own cluster" :title-color="BLUE"
        />
        <div class="note">J<sub>w</sub> adds up the squared length of every spoke</div>
      </div>
      <div class="col">
        <ClusterPlot
          :X="data.X" :labels="run.labels" :domain="dom" :point-size="2.4" :point-alpha="0.18"
          :edges="between" :crosses="[...centres, { x: m[0], y: m[1], color: INK, size: 11 }]"
          :tags="[...counts, { x: m[0], y: m[1] - 0.5, text: 'm', color: INK, size: 14 }]"
          title="J<sub>b</sub>: each centre m<sub>i</sub> to the centre m of all the data" :title-color="GREEN"
        />
        <div class="note">J<sub>b</sub> adds up each squared spoke n<sub>i</sub> times, once per point of the cluster</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="k" :min="1" :max="10" :step="1" label="K, clusters" :digits="0" :color="INK" />
      <Readout
        :items="[
          { label: 'J<sub>w</sub>', value: score.jw.toFixed(0), color: BLUE },
          { label: 'J<sub>b</sub>', value: score.jb.toFixed(0), color: GREEN },
          { label: 'J<sub>w</sub> + J<sub>b</sub>', value: (score.jw + score.jb).toFixed(0) },
        ]"
      />
      <span class="note">Raise K: the spokes on the left shorten, the right gains spokes, and the sum does not move.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 1.6rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.col .note { text-align: center; }
.controls { display: flex; gap: 1.4rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
</style>
