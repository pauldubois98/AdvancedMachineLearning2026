<!-- kmeans_algorithm: Lloyd's algorithm one half-step at a time. "assign"
     recolours the points, "move" slides the crosses to the means, and the
     inertia under the panel falls at every step until it stops. -->
<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { blobs } from '../lib/data4'
import { assign, inertia, randomInit, kmeansPlusPlus, recentre } from '../lib/cluster'
import { BLUE, GREEN, GOLD, MUTED, clusterColor } from '../lib/theme'

const K = ref(3)
const seed = ref(4)
const smart = ref(false)
/** the run so far: a list of (centres, labels) half-steps */
const steps = ref<{ mu: number[][]; labels: number[] | null; what: string }[]>([])

const data = blobs([[-1.8, -1.1], [1.9, -0.8], [0.1, 1.9]], 0.55, 60, 23)
const dom: [number, number, number, number] = [-4.2, 4.2, -3.4, 3.8]

function reset() {
  const mu = smart.value
    ? kmeansPlusPlus(data.X, K.value, seed.value)
    : randomInit(data.X, K.value, seed.value)
  steps.value = [{ mu, labels: null, what: '1. initialise' }]
}
reset()
watch([K, seed, smart], reset)

const cur = computed(() => steps.value[steps.value.length - 1])
const done = computed(() => {
  const s = steps.value
  if (s.length < 3) return false
  const a = s[s.length - 1]
  const b = s[s.length - 3]
  return a.labels !== null && b.labels !== null &&
    a.mu.every((m, k) => Math.hypot(m[0] - b.mu[k][0], m[1] - b.mu[k][1]) < 1e-12)
})

function step() {
  if (done.value) return
  const last = cur.value
  if (last.labels === null) {
    steps.value = [...steps.value, { mu: last.mu, labels: assign(data.X, last.mu), what: '2. assign' }]
  } else {
    const mu = recentre(data.X, last.labels, last.mu)
    steps.value = [...steps.value, { mu, labels: last.labels, what: '3. move the centres' }]
    steps.value = [...steps.value, { mu, labels: assign(data.X, mu), what: '4. repeat' }]
  }
}
function run() {
  for (let i = 0; i < 40 && !done.value; i++) step()
}

const labels = computed(() => cur.value.labels)
const score = computed(() =>
  cur.value.labels ? inertia(data.X, cur.value.labels, cur.value.mu) : null,
)
const sweeps = computed(() => Math.floor((steps.value.length - 1) / 2))
/** the path each centre has walked, so the slide shows where it came from */
const trails = computed(() => {
  const out: { a: [number, number]; b: [number, number]; color: string; width: number; alpha: number; dash: number[] }[] = []
  for (let i = 1; i < steps.value.length; i++) {
    steps.value[i].mu.forEach((m, k) => {
      const p = steps.value[i - 1].mu[k]
      if (Math.hypot(m[0] - p[0], m[1] - p[1]) < 1e-9) return
      out.push({ a: p as [number, number], b: m as [number, number], color: clusterColor(k), width: 1.2, alpha: 0.55, dash: [4, 3] })
    })
  }
  return out
})
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="data.X" :labels="labels" :colors="labels ? null : data.X.map(() => MUTED)"
      :domain="dom" :point-size="2.8" :edges="trails"
      :crosses="cur.mu.map((m, k) => ({ x: m[0], y: m[1], color: clusterColor(k) }))"
      :title="cur.what" :title-color="done ? GREEN : BLUE"
    />
    <div class="right">
      <ol class="steps">
        <li :class="{ on: cur.what.startsWith('1') }">initialise K centres</li>
        <li :class="{ on: cur.what.startsWith('2') || cur.what.startsWith('4') }">
          assign every point to its nearest centre</li>
        <li :class="{ on: cur.what.startsWith('3') }">move each centre to the mean of its points</li>
        <li>repeat until nothing moves</li>
      </ol>
      <div class="row">
        <button class="btn" :disabled="done" @click="step">next half-step</button>
        <button class="btn" :disabled="done" @click="run">run to the end</button>
        <button class="btn" @click="reset">reset</button>
      </div>
      <Knob v-model="K" :min="2" :max="6" :step="1" label="K" :digits="0" :color="BLUE" />
      <Knob v-model="seed" :min="0" :max="30" :step="1" label="starting draw" :digits="0" :color="GOLD" />
      <Toggle v-model="smart" label="k-means++ seeding" :color="GREEN" />
      <Readout
        :items="[
          { label: 'full sweeps', value: String(sweeps) },
          { label: 'inertia', value: score === null ? 'not assigned yet' : score.toFixed(1), color: BLUE },
          { label: '', value: done ? 'converged: no point changes cluster' : '', color: GREEN },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.15fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.steps { margin: 0 0 0.3rem; padding-left: 1.3rem; font-size: 0.84rem; color: #9aa0a6; line-height: 1.6; }
.steps li.on { color: #1b1b1b; font-weight: 600; }
.row { display: flex; gap: 0.5rem; }
.btn {
  border: 1px solid #d8dadd; border-radius: 0.3rem; padding: 0.16rem 0.5rem;
  background: white; cursor: pointer; font-size: 0.8rem;
}
.btn:hover:not(:disabled) { border-color: #9aa0a6; }
.btn:disabled { opacity: 0.4; cursor: default; }
</style>
