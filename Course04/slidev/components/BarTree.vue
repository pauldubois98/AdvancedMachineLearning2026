<!-- HDBSCAN's condensed tree: one bar per cluster, as wide as the number of
     points still inside it and as tall as the stretch of lambda it survives. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFitBox } from '../lib/fitbox'
import { CondensedCluster } from '../lib/density'
import { INK, MUTED } from '../lib/theme'

const props = withDefaults(
  defineProps<{
    clusters: Map<number, CondensedCluster>
    lamMax: number
    colorOf?: ((cid: number) => string) | null
    /** the clusters HDBSCAN keeps, drawn with a ring round them */
    selected?: number[]
    labelOf?: ((cid: number, c: CondensedCluster) => string) | null
    yLabel?: string
    title?: string
    titleColor?: string
  }>(),
  {
    colorOf: null, selected: () => [], labelOf: null, yLabel: 'λ = 1/ε',
    title: '', titleColor: INK,
  },
)

const svg = ref<SVGSVGElement | null>(null)
const { W, H } = useFitBox(svg, 600, 320)
const pad = { l: 54, r: 10, t: 12, b: 16 }
const tx = (v: number) => pad.l + v * (W.value - pad.l - pad.r)
const ty = (v: number) => pad.t + Math.min(1, v / props.lamMax) * (H.value - pad.t - pad.b)

/** every cluster gets a horizontal slot, children inside their parent */
const pos = computed(() => {
  const out = new Map<number, number>()
  const walk = (cid: number, x0: number, x1: number) => {
    out.set(cid, (x0 + x1) / 2)
    const kids = props.clusters.get(cid)!.children
    if (!kids.length) return
    const total = kids.reduce((s, k) => s + props.clusters.get(k)!.size0, 0)
    let x = x0
    for (const k of kids) {
      const w = ((x1 - x0) * props.clusters.get(k)!.size0) / total
      walk(k, x, x + w)
      x += w
    }
  }
  walk(0, 0.06, 0.94)
  return out
})

const root = computed(() => props.clusters.get(0)!.size0)

/** a bar is a stack of slices: one per point that falls out along the way */
const bars = computed(() => {
  const out: { cid: number; x: number; y0: number; y1: number; half: number; color: string }[] = []
  for (const [cid, c] of props.clusters) {
    const lam1 = Math.min(c.lamDeath === c.lamBirth ? props.lamMax : c.lamDeath, props.lamMax)
    const falls = c.falls.filter((l) => l <= lam1)
    const ys = [c.lamBirth, ...falls, lam1]
    let remaining = c.size0
    const color = props.colorOf ? props.colorOf(cid) : MUTED
    for (let i = 0; i < ys.length - 1; i++) {
      out.push({
        cid,
        x: pos.value.get(cid)!,
        y0: ys[i],
        y1: ys[i + 1],
        half: (0.17 * remaining) / root.value,
        color,
      })
      if (i < falls.length) remaining -= 1
    }
  }
  return out
})

const joins = computed(() =>
  [...props.clusters.entries()]
    .filter(([, c]) => c.children.length)
    .map(([cid, c]) => {
      const xs = c.children.map((k) => pos.value.get(k)!)
      return {
        x0: Math.min(...xs),
        x1: Math.max(...xs),
        y: Math.min(c.lamDeath, props.lamMax),
        color: props.colorOf ? props.colorOf(cid) : MUTED,
      }
    }),
)

const tags = computed(() =>
  [...props.clusters.entries()]
    .map(([cid, c]) => {
      const text = props.labelOf ? props.labelOf(cid, c) : ''
      if (!text) return null
      const lam1 = Math.min(c.lamDeath === c.lamBirth ? props.lamMax : c.lamDeath, props.lamMax)
      return {
        x: pos.value.get(cid)!,
        y: (c.lamBirth + lam1) / 2,
        text,
        color: props.colorOf ? props.colorOf(cid) : INK,
      }
    })
    .filter(Boolean) as { x: number; y: number; text: string; color: string }[],
)

const rings = computed(() =>
  props.selected
    .map((cid) => {
      const c = props.clusters.get(cid)
      if (!c) return null
      const lam1 = Math.min(c.lamDeath === c.lamBirth ? props.lamMax : c.lamDeath, props.lamMax)
      const half = (0.17 * c.size0) / root.value
      return { x: pos.value.get(cid)!, y0: c.lamBirth, y1: lam1, half }
    })
    .filter(Boolean) as { x: number; y0: number; y1: number; half: number }[],
)

const ticks = computed(() => {
  const step = props.lamMax / 4
  return [0, step, 2 * step, 3 * step, 4 * step].map((v) => Number(v.toFixed(2)))
})
</script>

<template>
  <figure class="chart">
    <figcaption v-if="title" :style="{ color: titleColor }" v-html="title" />
    <svg ref="svg" :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none">
      <line :x1="pad.l" :x2="pad.l" :y1="pad.t" :y2="H - pad.b" :style="{ stroke: INK, strokeWidth: 1.1 }" />
      <template v-for="(t, i) in ticks" :key="`t${i}`">
        <line :x1="pad.l - 4" :x2="pad.l" :y1="ty(t)" :y2="ty(t)" :style="{ stroke: INK, strokeWidth: 1 }" />
        <g :transform="`translate(${pad.l - 7}, ${ty(t) + 4})`">
          <text class="tick end">{{ t }}</text>
        </g>
      </template>
      <rect
        v-for="(b, i) in bars" :key="`b${i}`"
        :x="tx(b.x - b.half)" :y="ty(b.y0)"
        :width="Math.max(0.6, tx(b.x + b.half) - tx(b.x - b.half))"
        :height="Math.max(0.4, ty(b.y1) - ty(b.y0))"
        :style="{ fill: b.color }"
      />
      <line
        v-for="(j, i) in joins" :key="`j${i}`"
        :x1="tx(j.x0)" :x2="tx(j.x1)" :y1="ty(j.y)" :y2="ty(j.y)"
        :style="{ stroke: j.color, strokeWidth: 1.2 }"
      />
      <rect
        v-for="(r, i) in rings" :key="`r${i}`"
        :x="tx(r.x - r.half) - 3" :y="ty(r.y0) - 3"
        :width="tx(r.x + r.half) - tx(r.x - r.half) + 6"
        :height="ty(r.y1) - ty(r.y0) + 6"
        rx="3"
        :style="{ fill: 'none', stroke: '#00ab0e', strokeWidth: 1.6, strokeDasharray: '4,3' }"
      />
      <g
        v-for="(t, i) in tags" :key="`g${i}`"
        :transform="`translate(${tx(t.x)}, ${ty(t.y) + 4})`"
      >
        <text
          :style="{ fill: t.color, fontSize: '10.5px', textAnchor: 'middle', paintOrder: 'stroke', stroke: '#fff', strokeWidth: '3px', strokeLinejoin: 'round' }"
        >{{ t.text }}</text>
      </g>
      <text
        v-if="yLabel"
        :transform="`translate(13, ${(pad.t + H - pad.b) / 2}) rotate(-90)`"
        class="axis-label mid"
      >{{ yLabel }}</text>
    </svg>
  </figure>
</template>

<style scoped>
.chart { display: flex; flex-direction: column; height: 100%; min-height: 0; margin: 0; }
figcaption { text-align: center; font-size: 0.82rem; font-weight: 600; margin-bottom: 0.1rem; }
svg { width: 100%; flex: 1 1 0; min-height: 0; display: block; overflow: visible; }
.tick { font-size: 11px; fill: #1b1b1b; }
.axis-label { font-size: 12px; fill: #1b1b1b; }
.mid { text-anchor: middle; }
.end { text-anchor: end; }
</style>
