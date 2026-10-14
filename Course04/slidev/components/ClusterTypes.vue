<!-- cluster_types: three ideas of what a cluster is. The slider blurs the
     groups together, and each definition breaks down at its own moment. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { blobs, moons } from '../lib/data4'
import { assign } from '../lib/cluster'
import { dbscan } from '../lib/density'
import { BLUE, GREEN, PURPLE, clusterColor } from '../lib/theme'

const spread = ref(0.42)
const eps = ref(0.4)

const seeds: [number, number][] = [[-1.9, -1.1], [1.9, -0.9], [0.0, 1.9]]
const sep = computed(() => blobs(seeds, spread.value, 45, 7))
const proto = computed(() => blobs(seeds, spread.value * 1.6, 55, 3))
const protoLabels = computed(() => assign(proto.value.X, seeds.map((c) => [...c])))
const mo = moons(220, 0.06, 1, 2.2)
const dens = computed(() => dbscan(mo.X, eps.value, 6))

/** the lines from each point to the centre it was assigned to */
const spokes = computed(() =>
  proto.value.X.map((p, i) => ({
    from: p as [number, number],
    to: seeds[protoLabels.value[i]],
    color: clusterColor(protoLabels.value[i]),
    alpha: 0.3,
  })),
)
const dom: [number, number, number, number] = [-4.4, 4.4, -3.4, 3.6]
const nFound = computed(() => new Set(dens.value.labels.filter((l) => l >= 0)).size)
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div class="col">
        <ClusterPlot
          :X="sep.X" :labels="sep.y" :domain="dom" :point-size="2.8"
          title="well separated" :title-color="BLUE"
        />
        <div class="note">closer to each other than to anyone outside</div>
      </div>
      <div class="col">
        <ClusterPlot
          :X="proto.X" :labels="protoLabels" :domain="dom" :point-size="2.8" :spokes="spokes"
          :crosses="seeds.map((c, i) => ({ x: c[0], y: c[1], color: clusterColor(i) }))"
          title="prototype based" :title-color="GREEN"
        />
        <div class="note">each point belongs to its nearest centre</div>
      </div>
      <div class="col">
        <ClusterPlot
          :X="mo.X" :labels="dens.labels" :point-size="2.8"
          title="density based" :title-color="PURPLE"
        />
        <div class="note">a dense region, whatever shape it takes</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="spread" :min="0.25" :max="1.3" label="spread of the blobs" :color="BLUE" />
      <Knob v-model="eps" :min="0.1" :max="0.8" label="ε for the dense one" :color="PURPLE" />
      <Readout
        :items="[
          { label: 'dense regions found', value: String(nFound), color: nFound === 2 ? GREEN : '#c53030' },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.5rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; min-height: 0; }
.col .note { text-align: center; margin-top: 0.2rem; }
.controls { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.controls > :deep(.knob) { min-width: 12rem; }
</style>
