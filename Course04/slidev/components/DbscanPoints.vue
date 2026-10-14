<!-- dbscan_points: core, border, noise. The two sliders move points between
     the three roles, and the counts under them follow. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { distances } from '../lib/data4'
import { dbscan } from '../lib/density'
import { GOLD, GREEN, MUTED, RED } from '../lib/theme'

const eps = ref(0.55)
const minPts = ref(6)
const X = (() => {
  const rng = new Rng(12)
  const out: number[][] = []
  for (let i = 0; i < 55; i++) out.push([rng.normal(-0.8, 0.55), rng.normal(0, 0.55)])
  for (let i = 0; i < 30; i++) out.push([rng.normal(2.0, 0.45), rng.normal(0.4, 0.45)])
  for (let i = 0; i < 10; i++) out.push([rng.uniform(-2.6, 3.6), rng.uniform(-2.2, 2.2)])
  return out
})()
const D = distances(X)
const run = computed(() => dbscan(X, eps.value, minPts.value, D))
const colors = computed(() =>
  X.map((_, i) => (run.value.core[i] ? GREEN : run.value.border[i] ? GOLD : RED)),
)
const sizes = computed(() => X.map((_, i) => (run.value.core[i] ? 3.4 : 2.8)))
const firstCore = computed(() => run.value.core.findIndex(Boolean))
const nCore = computed(() => run.value.core.filter(Boolean).length)
const nBorder = computed(() => run.value.border.filter(Boolean).length)
const nNoise = computed(() => run.value.noise.filter(Boolean).length)
const dom: [number, number, number, number] = [-2.9, 3.9, -2.4, 2.4]
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :colors="colors" :sizes="sizes" :domain="dom"
      :circles="firstCore >= 0 ? [{ x: X[firstCore][0], y: X[firstCore][1], r: eps, color: GREEN, alpha: 0.1 }] : []"
      :title="`ε = ${eps.toFixed(2)},  MinPts = ${minPts}`"
    />
    <div class="right">
      <table class="plain">
        <tr><th>role</th><th>meaning</th><th>points</th></tr>
        <tr>
          <td :style="{ color: GREEN, fontWeight: 600 }">core</td>
          <td class="note">MinPts neighbours or more</td>
          <td :style="{ color: GREEN, fontWeight: 600 }">{{ nCore }}</td>
        </tr>
        <tr>
          <td :style="{ color: GOLD, fontWeight: 600 }">border</td>
          <td class="note">near a core point, but not one</td>
          <td :style="{ color: GOLD, fontWeight: 600 }">{{ nBorder }}</td>
        </tr>
        <tr>
          <td :style="{ color: RED, fontWeight: 600 }">noise</td>
          <td class="note">neither</td>
          <td :style="{ color: RED, fontWeight: 600 }">{{ nNoise }}</td>
        </tr>
      </table>
      <div class="controls">
        <Knob v-model="eps" :min="0.15" :max="1.4" label="ε" :color="GREEN" />
        <Knob v-model="minPts" :min="2" :max="25" :step="1" label="MinPts" :digits="0" :color="GOLD" />
      </div>
      <Readout
        :items="[
          { label: 'clusters', value: String(new Set(run.labels.filter((l) => l >= 0)).size) },
          { label: 'share called noise', value: `${((nNoise / X.length) * 100).toFixed(0)}%`, color: RED },
        ]"
      />
      <p class="note">A border point joins the cluster of a core neighbour but
        never passes its own neighbourhood on, which is why DBSCAN stops at the
        edge of a dense region instead of leaking out of it.</p>
      <p class="note">Raise MinPts with ε fixed and the core points thin out
        first; whole clusters then turn into
        <em :style="{ color: MUTED }">noise</em> at once.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.05fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.controls { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 1.2rem; }
</style>
