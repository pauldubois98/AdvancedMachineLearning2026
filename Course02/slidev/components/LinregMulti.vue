<!-- linreg_multi: two features, so the line becomes a plane. Turn the cloud
     around to see that the points sit on (and around) a flat sheet. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { fmt, wls } from '../lib/reg'
import { BLUE, GOLD, GRID, INK, MUTED, PURPLE } from '../lib/theme'

const az = ref(-60)
const el = ref(18)
const noise = ref(22)
const w2 = ref(14)
const data = computed(() => {
  const rng = new Rng(2)
  return Array.from({ length: 90 }, () => {
    const x1 = rng.uniform(25, 145), x2 = rng.uniform(0, 8)
    return [x1, x2, 1.7 * x1 + w2.value * x2 + 40 + rng.normal(0, noise.value)]
  })
})
const fit = computed(() => wls(data.value.map((p) => [1, p[0], p[1]]), data.value.map((p) => p[2])))
// normalise each axis to [-1, 1], then rotate and project
const zr = [40, 420]
const norm = (p: number[]) => [(p[0] - 85) / 60, (p[1] - 4) / 4, (p[2] - (zr[0] + zr[1]) / 2) / ((zr[1] - zr[0]) / 2)]
function proj(p: number[]): [number, number, number] {
  const [x, y, z] = norm(p)
  const a = (az.value * Math.PI) / 180, e = (el.value * Math.PI) / 180
  const xr = x * Math.cos(a) - y * Math.sin(a)
  const yr = x * Math.sin(a) + y * Math.cos(a)
  const sx = xr
  const sy = z * Math.cos(e) + yr * Math.sin(e)
  const depth = -yr * Math.cos(e) + z * Math.sin(e)
  return [300 + 190 * sx, 185 - 140 * sy, depth]
}
const plane = (x1: number, x2: number) => fit.value[0] + fit.value[1] * x1 + fit.value[2] * x2
const gridLines = computed(() => {
  const out: string[] = []
  for (let i = 0; i <= 6; i++) {
    const x1 = 25 + (120 * i) / 6
    out.push([0, 8].map((x2) => proj([x1, x2, plane(x1, x2)])).map((p, k) => `${k ? 'L' : 'M'}${p[0]},${p[1]}`).join(''))
    const x2 = (8 * i) / 6
    out.push([25, 145].map((x1) => proj([x1, x2, plane(x1, x2)])).map((p, k) => `${k ? 'L' : 'M'}${p[0]},${p[1]}`).join(''))
  }
  return out
})
const sheet = computed(() => [[25, 0], [145, 0], [145, 8], [25, 8]].map(([a, b]) => proj([a, b, plane(a, b)])).map((p) => `${p[0]},${p[1]}`).join(' '))
const pts = computed(() => data.value.map((p) => { const q = proj(p); return { x: q[0], y: q[1], d: q[2], above: p[2] > plane(p[0], p[1]) } }).sort((a, b) => a.d - b.d))
const axes = computed(() => {
  const o = [25, 0, zr[0]]
  return [
    { a: proj(o), b: proj([145, 0, zr[0]]), t: 'surface x₁' },
    { a: proj(o), b: proj([25, 8, zr[0]]), t: 'floor x₂' },
    { a: proj(o), b: proj([25, 0, zr[1]]), t: 'price y' },
  ]
})
</script>

<template>
  <div class="cmp">
    <div class="r2" style="grid-template-columns: 1.1fr 1fr; align-items: center">
      <svg viewBox="0 0 600 350" style="width: 100%; height: 100%">
        <line v-for="(a, i) in axes" :key="`a${i}`" :x1="a.a[0]" :y1="a.a[1]" :x2="a.b[0]" :y2="a.b[1]" :style="{ stroke: MUTED, strokeWidth: 1.2 }" />
        <text v-for="(a, i) in axes" :key="`t${i}`" :x="a.b[0]" :y="a.b[1] - 6" :style="{ fill: MUTED, fontSize: '13px', textAnchor: 'middle' }">{{ a.t }}</text>
        <polygon :points="sheet" :style="{ fill: PURPLE, fillOpacity: 0.12 }" />
        <path v-for="(d, i) in gridLines" :key="i" :d="d" :style="{ stroke: PURPLE, strokeWidth: 0.7, fill: 'none', strokeOpacity: 0.7 }" />
        <circle v-for="(p, i) in pts" :key="`p${i}`" :cx="p.x" :cy="p.y" r="3.6" :style="{ fill: p.above ? BLUE : '#8fb3dc', stroke: '#fff', strokeWidth: 0.6 }" />
      </svg>
      <div class="side" style="text-align: center">
        <p style="font-size: 1.1rem"><Tex formula="\hat y = w_1x_1 + w_2x_2 + \cdots + w_px_p + b" /></p>
        <p class="note" style="margin-top: 1rem">one weight per column; each weight = how much ŷ moves when this column moves by 1, all else fixed</p>
        <table class="plain" style="width: 80%; margin: 1rem auto">
          <tr><th></th><th>truth</th><th>fitted</th></tr>
          <tr><td>w₁ (per m²)</td><td>1.70</td><td :style="{ color: PURPLE }">{{ fmt(fit[1]) }}</td></tr>
          <tr><td>w₂ (per floor)</td><td>{{ fmt(w2, 1) }}</td><td :style="{ color: PURPLE }">{{ fmt(fit[2]) }}</td></tr>
          <tr><td>b</td><td>40</td><td :style="{ color: PURPLE }">{{ fmt(fit[0], 1) }}</td></tr>
        </table>
        <p :style="{ color: GOLD }">NB: units of the columns matter</p>
      </div>
    </div>
    <div class="foot">pale points lie under the fitted plane, dark ones above it</div>
    <div class="controls">
      <Knob v-model="az" :min="-180" :max="180" :step="1" :digits="0" label="turn" unit="°" :color="INK" />
      <Knob v-model="el" :min="-10" :max="80" :step="1" :digits="0" label="tilt" unit="°" :color="INK" />
      <Knob v-model="w2" :min="-10" :max="30" :step="0.5" :digits="1" label="true w₂" :color="PURPLE" />
      <Knob v-model="noise" :min="0" :max="60" :step="1" :digits="0" label="noise σ" :color="GRID" />
    </div>
  </div>
</template>
