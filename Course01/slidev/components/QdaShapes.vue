<!-- qda_shapes: with two covariances the quadratic term does not cancel, and
     the boundary is a conic: a line, an ellipse, a hyperbola. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { discriminant } from '../lib/stats'
import { boundary, regionColor } from '../lib/cls'
import type { Cov, Pt } from '../lib/geom'
import { BLUE, RED } from '../lib/theme'

const gap = ref(2.7)
const scale = ref(1)
const turn = ref(0)
const aniso = ref(1.25)
function preset(k: number) {
  if (k === 0) { gap.value = 2.7; scale.value = 1; turn.value = 0; aniso.value = 1.25 }
  if (k === 1) { gap.value = 0; scale.value = 3.4; turn.value = 0; aniso.value = 1 }
  if (k === 2) { gap.value = 0.6; scale.value = 1; turn.value = 90; aniso.value = 6.9 }
}
const rot = (l1: number, l2: number, t: number): Cov => {
  const c = Math.cos(t), s = Math.sin(t)
  return [l1 * c * c + l2 * s * s, (l1 - l2) * c * s, l1 * s * s + l2 * c * c]
}
const S1 = computed<Cov>(() => rot(0.32 * aniso.value, 0.32, 0))
const S2 = computed<Cov>(() => rot(0.32 * aniso.value * scale.value ** 2, 0.32 * scale.value ** 2, (turn.value * Math.PI) / 180))
const mu = computed<Pt[]>(() => [[-gap.value / 2, 0], [gap.value / 2, 0]])
const g = computed(() => discriminant(mu.value, [S1.value, S2.value], [0.5, 0.5]))
const kind = computed(() => {
  // the quadratic part of g is ½ xᵀ(Σ₁⁻¹ − Σ₂⁻¹)x: its eigenvalue signs name the conic
  const i1 = [S1.value[2], -S1.value[1], S1.value[0]].map((v) => v / (S1.value[0] * S1.value[2] - S1.value[1] ** 2))
  const i2 = [S2.value[2], -S2.value[1], S2.value[0]].map((v) => v / (S2.value[0] * S2.value[2] - S2.value[1] ** 2))
  const A = [i1[0] - i2[0], i1[1] - i2[1], i1[2] - i2[2]]
  const det = A[0] * A[2] - A[1] ** 2, tr = Math.abs(A[0]) + Math.abs(A[2]) + Math.abs(A[1])
  if (tr < 1e-6) return 'a line: equal Σ, the quadratic terms cancel (LDA)'
  if (Math.abs(det) < 1e-3 * tr * tr) return 'a parabola: the quadratic part is flat in one direction'
  return det > 0 ? 'an ellipse: one class is wider in every direction' : 'a hyperbola: each class is wider in a different direction'
})
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Exact class densities</b>, no data: class 1 (blue) is a Gaussian at the left centre; class 2 (red) at the right centre has its own scale and angle. The shading is the QDA decision; the ellipses are 1 and 2 standard deviations.</div>
    <Plane :domain="[-4.5, 4.5, -3.6, 3.6]" :field="g" :field-color="regionColor" :levels="[boundary(g)]"
      :ellipses="[{ mu: mu[0], S: S1, color: BLUE }, { mu: mu[1], S: S2, color: RED }]"
      :markers="[{ at: mu[0], color: BLUE, shape: 'x' }, { at: mu[1], color: RED, shape: 'x' }]" />
    <div class="foot">the boundary is <b>{{ kind }}</b>. Presets:
      <button class="pre" @click="preset(0)">equal Σ</button> <button class="pre" @click="preset(1)">different spread</button> <button class="pre" @click="preset(2)">different orientation</button></div>
    <div class="controls">
      <Knob v-model="gap" :min="0" :max="5" :step="0.05" label="distance between centres" color="#1b1b1b" />
      <Knob v-model="aniso" :min="1" :max="8" :step="0.05" label="elongation" color="#1b1b1b" />
      <Knob v-model="scale" :min="0.3" :max="3.5" :step="0.01" label="class 2: scale" :color="RED" />
      <Knob v-model="turn" :min="0" :max="180" :step="1" :digits="0" unit="°" label="class 2: angle" :color="RED" />
    </div>
  </div>
</template>

<style scoped>
.pre { border: 1px solid #d8dadd; border-radius: 0.3rem; padding: 0.05rem 0.45rem; background: white; cursor: pointer; font-size: 0.75rem; color: #1b1b1b; }
.pre:hover { border-color: #9aa0a6; }
</style>
