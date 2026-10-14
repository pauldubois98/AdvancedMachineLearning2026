<!-- inertia_defined: the spokes whose squared lengths are added up, and what
     happens to the total as K grows: it falls, always, down to zero at K = n. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { blobs } from '../lib/data4'
import { kmeans } from '../lib/cluster'
import { BLUE, GOLD, GREEN, RED, clusterColor } from '../lib/theme'

const K = ref(3)
const data = blobs([[-1.9, -1.0], [1.9, -0.8], [0.0, 1.9]], 0.56, 40, 8)
const dom: [number, number, number, number] = [-4.2, 4.2, -3.2, 3.6]

const run = computed(() => kmeans(data.X, K.value, 0, 8))
const spokes = computed(() =>
  data.X.map((p, i) => ({
    from: p as [number, number],
    to: run.value.mu[run.value.labels[i]] as [number, number],
    color: clusterColor(run.value.labels[i]),
    alpha: 0.45,
  })),
)
/** one k-means per K, so the curve is measured and not drawn by hand */
const curve = computed(() =>
  Array.from({ length: 12 }, (_, i) => {
    const k = i + 1
    return [k, kmeans(data.X, k, 1, 5).inertia] as [number, number]
  }),
)
const here = computed(() => curve.value[K.value - 1])
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="data.X" :labels="run.labels" :domain="dom" :point-size="3.2" :spokes="spokes"
      :crosses="run.mu.map((m, k) => ({ x: m[0], y: m[1], color: clusterColor(k) }))"
      title="every point pulls on its own centre" :title-color="BLUE"
    />
    <div class="right">
      <LineChart
        :series="[{ points: curve, color: BLUE, width: 2.4 }]"
        :dots="[{ x: here[0], y: here[1], color: GOLD, r: 5 }]"
        :vlines="[{ x: K, color: GOLD, dash: '' }]"
        :x-domain="[0.6, 12.4]" :y-domain="[0, curve[0][1] * 1.06]"
        :x-ticks="[1, 3, 5, 7, 9, 11]"
        x-label="K" y-label="inertia"
        title="inertia falls at every K" :title-color="BLUE"
      />
      <div class="formula"><Tex display formula='J_w = \sum_{k=1}^{K} \sum_{x_i \in C_k} \|x_i - \mu_k\|^2' /></div>
      <Knob v-model="K" :min="1" :max="12" :step="1" label="K" :digits="0" :color="GOLD" />
      <Readout
        :items="[
          { label: 'inertia', value: here[1].toFixed(1), color: GOLD },
          { label: 'drop from K − 1', value: K > 1 ? (curve[K - 2][1] - here[1]).toFixed(1) : 'n/a', color: GREEN },
        ]"
      />
      <p class="note">It is what k-means minimises, and it only ever falls with
        K, so it cannot choose K for you: at K = n it is exactly
        <em class="hl-red">0</em>.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 0.95fr 1.1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: grid; grid-template-rows: 1fr auto auto auto auto; gap: 0.35rem; min-height: 0; }
.formula { text-align: center; font-size: 0.86rem; }
</style>
