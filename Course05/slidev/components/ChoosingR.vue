<!-- choosing_r: a larger r always fits better, so the error alone never
     picks r. The fits are precomputed (HALS from NNDSVD on the 300 small
     faces); pick r to see its parts, a face rebuilt from them, and which parts
     come back when the fit is restarted from another start. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { SIDE, choosing, face } from '../lib/data5'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const STABLE = 0.8
const RS = choosing.map((f) => f.r)
const r = ref('12')
const j = ref(6)
const fit = computed(() => choosing.find((f) => f.r === Number(r.value))!)
const errPts = choosing.map((f) => [f.r, 100 * f.err] as [number, number])
const stablePts = choosing.map((f) => [f.r, 100 * f.match.filter((m) => m > STABLE).length / f.r] as [number, number])
const at = computed(() => RS.indexOf(fit.value.r))
// unstable parts are drawn pale
const parts = computed(() => fit.value.W.map((w, k) => (fit.value.match[k] > STABLE ? w : w.map((v) => v * 0.22))))
const nStable = computed(() => fit.value.match.filter((m) => m > STABLE).length)
const rebuilt = computed(() => {
  const { W, H } = fit.value
  const out = new Float64Array(SIDE * SIDE)
  W.forEach((w, k) => { const h = H[k][j.value]; for (let q = 0; q < out.length; q++) out[q] += w[q] * h })
  return out
})
const faceErr = computed(() => {
  const x = face(j.value)
  let a = 0, b = 0
  for (let q = 0; q < x.length; q++) { a += (x[q] - rebuilt.value[q]) ** 2; b += x[q] ** 2 }
  return 100 * Math.sqrt(a / b)
})
</script>

<template>
  <div class="wrap">
    <div class="note top">NMF cannot determine best r</div>
    <div class="body">
      <div class="charts">
        <LineChart
          :series="[{ points: errPts, color: BLUE, width: 2.4 }]"
          :dots="[...errPts.map(([x, y]) => ({ x, y, color: BLUE, r: 4 })), { x: errPts[at][0], y: errPts[at][1], color: BLUE, r: 8, hollow: true }]"
          :x-domain="[0, 50]" :y-domain="[0, 20]" x-label="r" y-label="relative error (%)" :x-ticks="[0, 10, 20, 30, 40, 50]" :y-ticks="[0, 5, 10, 15, 20]"
          title="300 faces: the error keeps falling" :unit-height="210" :title-color="BLUE"
        />
        <LineChart
          :series="[{ points: stablePts, color: GREEN, width: 2.4 }]"
          :dots="[...stablePts.map(([x, y]) => ({ x, y, color: GREEN, r: 4 })), { x: stablePts[at][0], y: stablePts[at][1], color: GREEN, r: 8, hollow: true }]"
          :x-domain="[0, 50]" :y-domain="[0, 105]" x-label="r" y-label="parts found again (%)" :x-ticks="[0, 10, 20, 30, 40, 50]" :y-ticks="[0, 25, 50, 75, 100]"
          title="but fewer parts survive a restart" :unit-height="210" :title-color="GREEN"
        />
      </div>
      <div class="mid">
        <Tiles :items="parts" :side="SIDE" ramp="grayr" :vmin="0" :vmax="1" :gap="2" :title="`the ${fit.r} parts: ${nStable} found again, ${fit.r - nStable} pale`" :title-color="INK" />
        <div class="pair">
          <Tiles :items="[face(j)]" :side="SIDE" ramp="gray" :vmin="0" :vmax="1" caption="face" />
          <Tiles :items="[rebuilt]" :side="SIDE" ramp="gray" :vmin="0" :vmax="1" :caption="`rebuilt from ${fit.r} parts:<br>${faceErr.toFixed(1)}% error`" />
        </div>
      </div>
      <div class="side">
        <div class="h" :style="{ color: RED }">Larger r always fits better</div>
        <div class="h mt" :style="{ color: GREEN }">Choose r with:</div>
        <p>— Elbow (if there is one)</p>
        <p>— Stability (unstable components can be discarded)</p>
        <p>— Domain knowledge (e.g. 3 notes/materials)</p>
      </div>
    </div>
    <div class="controls">
      <Choice v-model="r" label="r" :options="RS.map((v) => ({ value: String(v), label: String(v), color: BLUE }))" />
      <Knob v-model="j" :min="0" :max="299" :step="1" label="face" :digits="0" :color="INK" />
    </div>
    <div class="credit">data: Olivetti faces, AT&amp;T Cambridge (shrunk to 32 × 32); HALS from NNDSVD, 150 passes; a part is found again when a fit from a random start has one within cosine {{ STABLE }}</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1.15fr 0.9fr; gap: 1.4rem; min-height: 0; }
.charts { display: grid; grid-template-rows: 1fr 1fr; gap: 0.4rem; min-height: 0; }
.mid { display: grid; grid-template-rows: 1.4fr 1fr; gap: 0.4rem; min-height: 0; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 0.6rem; min-height: 0; }
.side { align-self: center; }
.side .h { font-weight: 700; }
.side .mt { margin-top: 1.6rem; }
.side p { margin: 0.4rem 0; font-size: 0.85rem; }
</style>
