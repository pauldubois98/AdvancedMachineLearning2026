<!-- penalty_geometry: the constrained view. The solution is where the loss
     contours, centred at β̂_LS, first touch the ball R(β) ≤ t. Move β̂_LS or
     shrink the ball: the lasso's corner keeps catching the axes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { fmt } from '../lib/reg'
import type { Pt } from '../lib/geom'
import { BLUE, GREEN, GRID, INK, MUTED, RED } from '../lib/theme'

const bx = ref(1.55)
const by = ref(1.05)
const t = ref(1)
const alpha = ref(0.6)
const A = [[1.0, 0.75], [0.75, 1.3]]
const loss = (x: number, y: number) => {
  const u = x - bx.value, v = y - by.value
  return A[0][0] * u * u + 2 * A[0][1] * u * v + A[1][1] * v * v
}
const TH = Array.from({ length: 1440 }, (_, i) => (2 * Math.PI * i) / 1440)
function ball(kind: string): Pt[] {
  return TH.map((th) => {
    const c = Math.cos(th), s = Math.sin(th)
    let r: number
    if (kind === 'ridge') r = t.value
    else if (kind === 'lasso') r = t.value / (Math.abs(c) + Math.abs(s))
    else {
      const a = alpha.value, quad = (1 - a) / 2, lin = a * (Math.abs(c) + Math.abs(s))
      const lev = a * t.value + quad * t.value * t.value // passes through (t, 0)
      r = quad < 1e-9 ? lev / lin : (-lin + Math.sqrt(lin * lin + 4 * quad * lev)) / (2 * quad)
    }
    return [r * c, r * s]
  })
}
const inside = (kind: string, p: Pt) => {
  const a = Math.abs(p[0]), b = Math.abs(p[1])
  if (kind === 'ridge') return Math.hypot(a, b) <= t.value
  if (kind === 'lasso') return a + b <= t.value
  const al = alpha.value
  return al * (a + b) + ((1 - al) / 2) * (a * a + b * b) <= al * t.value + ((1 - al) / 2) * t.value ** 2
}
const panels = computed(() => [
  { kind: 'ridge', color: BLUE, title: 'ridge  ‖β‖₂ ≤ t', remark: 'a circle has no corner' },
  { kind: 'lasso', color: GREEN, title: 'lasso  ‖β‖₁ ≤ t', remark: 'the corner sits on the axis' },
  { kind: 'enet', color: RED, title: `elastic net, α = ${alpha.value.toFixed(2)}`, remark: 'a corner, and a rounded edge' },
].map((p) => {
  const B = ball(p.kind)
  const ls: Pt = [bx.value, by.value]
  let sol: Pt = ls
  if (!inside(p.kind, ls)) {
    let best = Infinity
    for (const q of B) { const v = loss(q[0], q[1]); if (v < best) { best = v; sol = q } }
  }
  const L0 = Math.max(loss(sol[0], sol[1]), 1e-4)
  const sparse = Math.abs(sol[0]) < 0.01 || Math.abs(sol[1]) < 0.01
  return { ...p, B, sol, sparse, levels: [1, 2.4, 4.6].map((k) => ({ f: loss, level: L0 * k, color: MUTED, width: 1.2 })) }
}))
const dom: [number, number, number, number] = [-1.2, 2.6, -1.2, 2.3]
const axes = [{ a: [-3, 0] as Pt, b: [3, 0] as Pt, color: GRID, width: 1 }, { a: [0, -3] as Pt, b: [0, 3] as Pt, color: GRID, width: 1 }]
</script>

<template>
  <div class="cmp">
    <div class="r3">
      <Plane v-for="p in panels" :key="p.kind" :domain="dom" :segments="axes" :levels="p.levels"
        :polys="[{ pts: p.B, fill: p.color, alpha: 0.1, stroke: p.color, width: 2.2 }]"
        :markers="[{ at: [bx, by], color: INK, shape: 'x', size: 6 }, { at: p.sol, color: p.color, shape: 'dot', size: 6 }]"
        :texts="[{ at: [bx + 0.1, by + 0.12], text: 'β̂_LS', color: INK, size: 13 }]"
        :title="p.title" :title-color="p.color"
        :caption="`${p.remark}<br>solution (${fmt(p.sol[0])}, ${fmt(p.sol[1])})${p.sparse ? ': <b style=&quot;color:#00ab0e&quot;>one coefficient is 0</b>' : ''}`" />
    </div>
    <div class="foot">solution is where the loss contours first touch the ball</div>
    <div class="controls">
      <Knob v-model="bx" :min="-1" :max="2.4" :step="0.01" label="β̂_LS,1" :color="INK" />
      <Knob v-model="by" :min="-1" :max="2" :step="0.01" label="β̂_LS,2" :color="INK" />
      <Knob v-model="t" :min="0.1" :max="2" :step="0.01" label="budget t" :color="MUTED" />
      <Knob v-model="alpha" :min="0" :max="1" :step="0.01" label="elastic net α" :color="RED" />
    </div>
  </div>
</template>
