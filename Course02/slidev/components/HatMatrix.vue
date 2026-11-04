<!-- hat_matrix: ŷ is the orthogonal projection of y on the span of the
     columns; β̂ is the recipe that mixes the columns into ŷ. Move y, or the
     second column, and the projection follows. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { fmt } from '../lib/reg'
import { BLUE, GREEN, GRID, INK, MUTED, PURPLE, RED } from '../lib/theme'

const ya = ref(2.74) // y's coordinates: along x1, along the depth, height
const yb = ref(0.7)
const yh = ref(2.3)
const ang = ref(90) // the angle between the two columns, in the plane

const iso = (v: number[]): [number, number] => [80 + 105 * (v[0] + 0.46 * v[1]), 330 - 105 * (0.3 * v[1] + v[2])]
const c1 = [2.55, 0, 0]
const c2 = computed(() => [2.0 * Math.cos((ang.value * Math.PI) / 180), 2.0 * Math.sin((ang.value * Math.PI) / 180), 0])
// the plane is z = 0: x̂ = (ya, yb, 0) = b1 c1 + b2 c2
const beta = computed(() => {
  const b2 = yb.value / c2.value[1]
  const b1 = (ya.value - b2 * c2.value[0]) / c1[0]
  return [b1, b2]
})
const y = computed(() => [ya.value, yb.value, yh.value])
const yhat = computed(() => [ya.value, yb.value, 0])
const P = (v: number[]) => iso(v).join(',')
const sheet = computed(() => {
  const C2 = c2.value
  const pts = [[-0.42, -0.42], [1.62, -0.42], [1.62, 1.45], [-0.42, 1.45]].map(([s, t]) => [s * c1[0] + t * C2[0], s * c1[1] + t * C2[1], 0])
  return pts.map(P).join(' ')
})
const m1 = computed(() => [beta.value[0] * c1[0], 0, 0])
const m2 = computed(() => c2.value.map((v) => v * beta.value[1]))
// the right angle at ŷ, drawn in screen space
const corner = computed(() => {
  const f = iso(yhat.value), o = iso([0, 0, 0])
  let ax = o[0] - f[0], ay = o[1] - f[1]
  const L = Math.hypot(ax, ay) || 1
  ax = (16 * ax) / L; ay = (16 * ay) / L
  const up = iso([ya.value, yb.value, Math.sign(yh.value || 1) * 0.15])
  const ux = up[0] - f[0], uy = up[1] - f[1]
  return `M${f[0] + ax},${f[1] + ay} L${f[0] + ax + ux},${f[1] + ay + uy} L${f[0] + ux},${f[1] + uy}`
})
const arrowHead = (a: number[], b: number[]) => {
  const A = iso(a), B = iso(b), t = Math.atan2(B[1] - A[1], B[0] - A[0])
  return `${B[0]},${B[1]} ${B[0] - 11 * Math.cos(t - 0.4)},${B[1] - 11 * Math.sin(t - 0.4)} ${B[0] - 11 * Math.cos(t + 0.4)},${B[1] - 11 * Math.sin(t + 0.4)}`
}
const vec = (a: number[], b: number[], color: string, w = 2.6) => ({ a: iso(a), b: iso(b), head: arrowHead(a, b), color, w })
const arrows = computed(() => [
  vec([0, 0, 0], c1, BLUE, 2), vec([0, 0, 0], c2.value, BLUE, 2),
  vec([0, 0, 0], y.value, PURPLE), vec([0, 0, 0], yhat.value, GREEN), vec(yhat.value, y.value, RED),
])
const xte = computed(() => {
  // X^T e: e = (0, 0, yh) is orthogonal to any column in the plane z = 0
  return [c1[2] * yh.value, c2.value[2] * yh.value]
})
</script>

<template>
  <div class="cmp">
    <div class="r2" style="grid-template-columns: 1fr 1.5fr; align-items: center">
      <div class="side">
        <p style="font-size: 1.05rem"><Tex formula="\hat y = Hy \qquad H = X(X^TX)^{-1}X^T" /></p>
        <p class="note">orthogonal projection on the model domain</p>
        <p :style="{ color: GREEN, marginTop: '0.9rem' }">ŷ = β̂₁ x₁ + β̂₂ x₂ = <b>{{ fmt(beta[0]) }}</b> x₁ + <b>{{ fmt(beta[1]) }}</b> x₂</p>
        <p :style="{ color: RED }">e ⊥ columns of X: Xᵀe = ({{ fmt(xte[0]) }}, {{ fmt(xte[1]) }})</p>
        <p :style="{ color: RED }">‖e‖ = {{ fmt(Math.abs(yh)) }}, the shortest distance from y to the plane</p>
        <p class="note" style="margin-top: 0.9rem">tilt the columns: β̂ changes, ŷ does not. The projection depends on the span only.</p>
      </div>
      <svg viewBox="0 0 640 380" style="width: 100%; height: 100%">
        <polygon :points="sheet" :style="{ fill: '#eef3fa', stroke: BLUE, strokeWidth: 2 }" />
        <line :x1="iso(m1)[0]" :y1="iso(m1)[1]" :x2="iso(yhat)[0]" :y2="iso(yhat)[1]" :style="{ stroke: GRID, strokeWidth: 1.4, strokeDasharray: '5,4' }" />
        <line :x1="iso(m2)[0]" :y1="iso(m2)[1]" :x2="iso(yhat)[0]" :y2="iso(yhat)[1]" :style="{ stroke: GRID, strokeWidth: 1.4, strokeDasharray: '5,4' }" />
        <path :d="corner" :style="{ stroke: RED, strokeWidth: 1.3, fill: 'none' }" />
        <template v-for="(a, i) in arrows" :key="i">
          <line :x1="a.a[0]" :y1="a.a[1]" :x2="a.b[0]" :y2="a.b[1]" :style="{ stroke: a.color, strokeWidth: a.w }" />
          <polygon :points="a.head" :style="{ fill: a.color }" />
        </template>
        <text :x="iso(c1)[0] + 8" :y="iso(c1)[1] + 18" :style="{ fill: BLUE, fontSize: '16px' }">x₁</text>
        <text :x="iso(c2)[0] - 26" :y="iso(c2)[1]" :style="{ fill: BLUE, fontSize: '16px' }">x₂</text>
        <text :x="iso(y)[0] + 10" :y="iso(y)[1]" :style="{ fill: PURPLE, fontSize: '18px' }">y</text>
        <text :x="iso(yhat)[0] + 14" :y="iso(yhat)[1] + 20" :style="{ fill: GREEN, fontSize: '16px' }">ŷ = Xβ̂</text>
        <text :x="iso([ya, yb, yh / 2])[0] + 10" :y="iso([ya, yb, yh / 2])[1]" :style="{ fill: RED, fontSize: '15px' }">e = y − ŷ</text>
        <text :x="iso([0.3 * c1[0] - 0.42 * c2[0], -0.42 * c2[1], 0])[0]" :y="iso([0.3 * c1[0], -0.42 * c2[1], 0])[1] + 26" :style="{ fill: BLUE, fontSize: '14px' }">span of the columns of X</text>
      </svg>
    </div>
    <div class="controls">
      <Knob v-model="ya" :min="-0.5" :max="4" :step="0.01" label="y along x₁" :color="PURPLE" />
      <Knob v-model="yb" :min="0" :max="2.6" :step="0.01" label="y in depth" :color="PURPLE" />
      <Knob v-model="yh" :min="-1" :max="2.8" :step="0.01" label="y off the plane" :color="RED" />
      <Knob v-model="ang" :min="35" :max="145" :step="1" :digits="0" label="angle x₁, x₂" unit="°" :color="BLUE" />
    </div>
  </div>
</template>
