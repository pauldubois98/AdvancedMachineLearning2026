<!-- dbscan_idea: the two thresholds. eps says what "nearby" means, MinPts
     what "crowded" means, and a cluster is a dense region. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { distances } from '../lib/data4'
import { dbscan } from '../lib/density'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const eps = ref(0.55)
const minPts = ref(5)
const X = (() => {
  const rng = new Rng(9)
  const out: number[][] = []
  for (let i = 0; i < 40; i++) out.push([rng.normal(-0.6, 0.55), rng.normal(0.2, 0.55)])
  for (let i = 0; i < 18; i++) out.push([rng.normal(2.1, 0.3), rng.normal(0.5, 0.3)])
  for (let i = 0; i < 8; i++) out.push([rng.uniform(-2.5, 3.5), rng.uniform(-2.2, 2.4)])
  return out
})()
const D = distances(X)
const probe = [3, X.length - 1]
const run = computed(() => dbscan(X, eps.value, minPts.value, D))
const counts = computed(() => probe.map((i) => run.value.counts[i]))
const dom: [number, number, number, number] = [-3.0, 4.0, -2.4, 2.6]
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :labels="run.labels" :point-size="3" :domain="dom"
      :circles="probe.map((i, k) => ({ x: X[i][0], y: X[i][1], r: eps, color: k === 0 ? GREEN : RED, alpha: 0.12 }))"
      :tags="probe.map((i, k) => ({
        x: X[i][0], y: X[i][1] - eps - 0.28,
        text: `${counts[k]} within ε ${counts[k] >= minPts ? '→ core' : '→ not core'}`,
        color: k === 0 ? GREEN : RED, size: 11.5,
      }))"
      title="two neighbourhoods: one crowded, one not" :title-color="INK"
    />
    <div class="right">
      <p><em class="hl-blue">ε</em>: the threshold for "nearby"<br />
        <span class="small"><Tex display formula='N_\varepsilon(x_i) = \{ z : d(x_i, z) \leq \varepsilon \}' /></span></p>
      <p><em class="hl-green">MinPts</em>: the threshold for "crowded"<br />
        <span class="small">x<sub>i</sub> is a core point if |N<sub>ε</sub>(x<sub>i</sub>)| ≥ MinPts</span></p>
      <div class="controls">
        <Knob v-model="eps" :min="0.12" :max="1.6" label="ε" :color="BLUE" />
        <Knob v-model="minPts" :min="2" :max="20" :step="1" label="MinPts" :digits="0" :color="GREEN" />
      </div>
      <Readout
        :items="[
          { label: 'core points', value: String(run.core.filter(Boolean).length), color: GREEN },
          { label: 'clusters', value: String(new Set(run.labels.filter((l) => l >= 0)).size), color: BLUE },
          { label: 'noise', value: String(run.noise.filter(Boolean).length), color: RED },
        ]"
      />
      <p class="note">A cluster is a dense region, so <em class="hl-red">no K is
        asked for</em>: the two thresholds decide how many there are.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.05fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.55rem; justify-content: center; font-size: 0.88rem; }
.right p { margin: 0; line-height: 1.5; }
.small { font-size: 0.78rem; }
.controls { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 1.2rem; }
</style>
