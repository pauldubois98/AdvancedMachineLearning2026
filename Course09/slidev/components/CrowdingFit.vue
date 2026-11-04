<!-- crowding, part 1: k neighbours at distance 1 from a point, all at least
     1 apart. In 2-D up to six fit; on a line only two do, and the rest are
     pushed out. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { COMP, GRID, HIGH, LOW, RED } from '../lib/theme'
import type { Pt } from '../lib/geom'

const kk = ref(6)
const k = computed(() => Math.round(kk.value))
const cols = computed(() => Array.from({ length: k.value }, (_, i) => COMP[i % 5]))
const ring = computed<Pt[]>(() => Array.from({ length: k.value }, (_, i) => {
  const t = (2 * Math.PI * i) / k.value
  return [Math.cos(t), Math.sin(t)]
}))
const side = computed(() => 2 * Math.sin(Math.PI / k.value)) // the gap between two ring neighbours
const segs = computed(() => [
  ...ring.value.map((p) => ({ a: [0, 0] as Pt, b: p, color: GRID, width: 1 })),
  // two ring neighbours closer than 1: they would have to be farther apart
  ...(side.value < 0.999 ? ring.value.map((p, i) => ({ a: p, b: ring.value[(i + 1) % k.value], color: RED, width: 2 })) : []),
])
// the line: alternate sides at distance 1, 1, 2, 2, 3, ... (the best one can
// do with every neighbour at least 1 from the others)
const line = computed<Pt[]>(() => Array.from({ length: k.value }, (_, i) => [(i % 2 ? -1 : 1) * (Math.floor(i / 2) + 1), 0]))
const far = computed(() => Math.ceil(k.value / 2))
const L = computed(() => Math.max(3.4, far.value + 0.6))
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> a point (the star) and k neighbours, all at distance 1 from it and at least 1 from each other. <b>Top, in 2-D:</b> the neighbours sit evenly on the unit circle; from 7 on, two of them come closer than 1 to each other, and red lines join those pairs. <b>Bottom, on a line:</b> the best a 1-D map can do is one neighbour on each side at distance 1, then the next ones at 2, 3, and so on.</div>
    <div class="stack" style="grid-template-rows: 1fr 0.34fr">
      <Plane :X="ring" :colors="cols" :size="8" :segments="segs"
        :markers="[{ at: [0, 0], color: RED, shape: 'star', size: 11 }]" :domain="[-1.5, 1.5, -1.5, 1.5]"
        :title="`2-D: ${k} neighbours at distance 1, ${side.toFixed(2)} apart`" :title-color="side < 0.999 ? RED : HIGH" />
      <Plane :X="line" :colors="cols" :size="6" :equal="false"
        :segments="[{ a: [-L, 0], b: [L, 0], color: GRID }]"
        :markers="[{ at: [0, 0], color: RED, shape: 'star', size: 9 }]" :domain="[-L - 0.2, L + 0.2, -0.6, 0.6]"
        :title="`1-D: only two at distance 1, the farthest at ${far}`" :title-color="LOW" />
    </div>
    <div class="foot">{{ k }} neighbours at the same distance <b>{{ k <= 6 ? 'fit' : 'no longer fit' }}</b> in 2-D, but on a line only two do and the others are pushed out to distance {{ far }}:
      fewer dimensions leave less room for neighbours.</div>
    <div class="controls"><Knob v-model="kk" :min="2" :max="12" :step="1" :digits="0" label="neighbours" :color="RED" /></div>
  </div>
</template>
