<!-- gmm_anomaly: a fitted mixture scores any new point by its density. The
     red line is the q% contour of the training density; click to drop a
     point of your own. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { em2, kmeansStart, mixPdf2, sampleMix2, TWO_BLOBS, type Pt } from '../lib/gmm'
import { Rng } from '../lib/rng'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const { X } = sampleMix2(TWO_BLOBS, 280, 3)
const fit = em2(X, kmeansStart(X, 2, 0), 120).at(-1)!
const dens = X.map((x) => mixPdf2(x, fit)).sort((a, b) => a - b)
const q = ref(2)
const thr = computed(() => dens[Math.max(0, Math.floor((q.value / 100) * dens.length) - 1)])
const rng = new Rng(9)
const stars = ref<Pt[]>(Array.from({ length: 14 }, () => [rng.uniform(-3.4, 3.4), rng.uniform(-2.6, 2.6)] as Pt))
const mine = ref<Pt | null>(null)
const flagged = computed(() => stars.value.filter((s) => mixPdf2(s, fit) < thr.value).length)
const ldmax = Math.log(Math.max(...dens))
function blues(v: number): [number, number, number] {
  const t = Math.min(1, Math.max(0, (v - (ldmax - 9)) / 9))
  return [Math.round(247 - t * 239), Math.round(251 - t * 203), Math.round(255 - t * 148)]
}
const field = (x: number, y: number) => Math.log(Math.max(mixPdf2([x, y], fit), 1e-12))
</script>

<template>
  <div class="wrap">
    <div class="note top">A mixture gives every point a score: its density. Click the map to drop a point.</div>
    <div class="body">
      <Plane
        :X="X" colors="#ffffff" :size="2" :alpha="0.6" :domain="[-3.6, 3.6, -2.8, 2.8]"
        :field="field" :field-color="blues" :field-res="90"
        :levels="[{ f: (x: number, y: number) => mixPdf2([x, y], fit), level: thr, color: RED, width: 2 }]"
        :markers="[
          ...stars.map((s) => ({ at: s, color: mixPdf2(s, fit) < thr ? RED : GREEN, shape: 'star', size: 8 })),
          ...(mine ? [{ at: mine, color: INK, shape: 'ring', size: 8 }] : []),
        ]"
        pickable @pick="(x: number, y: number) => (mine = [x, y])"
      />
      <div class="side">
        <div class="h" :style="{ color: BLUE }">Novelty detection, for free</div>
        <p>— score a new point by its density f(x) = p₁ f₁(x) + ⋯ + p<sub>K</sub> f<sub>K</sub>(x)</p>
        <p>— the red line is the {{ q }}% contour of the training density: {{ q }}% of the training points fall outside it</p>
        <p>— <b>{{ flagged }}</b> of the {{ stars.length }} new stars fall outside it (red)</p>
        <p v-if="mine" class="big">your point: log f = {{ Math.log(mixPdf2(mine, fit)).toFixed(2) }},
          <b :style="{ color: mixPdf2(mine, fit) < thr ? RED : GREEN }">{{ mixPdf2(mine, fit) < thr ? 'flagged' : 'normal' }}</b></p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="q" :min="0.5" :max="20" :step="0.5" label="contour level q" unit="%" :digits="1" :color="RED" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
.big { margin-top: 0.6rem; }
</style>
