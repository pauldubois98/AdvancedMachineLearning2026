<!-- A dendrogram drawn from a linkage: one staple per merge, height on the y
     axis, plus the horizontal lines the cut slides put across it. -->
<script setup lang="ts">
import { computed } from 'vue'
import { Linkage, dendrogram } from '../lib/hier'
import { GRID, INK, MUTED } from '../lib/theme'

const props = withDefaults(
  defineProps<{
    Z: Linkage
    /** colour per merge, keyed by the cluster id n + r of that merge */
    colorOf?: ((id: number, height: number) => string) | null
    cuts?: { y: number; color?: string; label?: string; dash?: string }[]
    leafLabels?: string[] | null
    yLabel?: string
    title?: string
    titleColor?: string
    yMax?: number | null
    width?: number
    yTicks?: number[] | null
  }>(),
  {
    colorOf: null, cuts: () => [], leafLabels: null, yLabel: 'merge distance',
    title: '', titleColor: INK, yMax: null, width: 1.2, yTicks: null,
  },
)

const W = 600
const H = 320
const pad = computed(() => ({
  l: 46, r: 10, t: 10, b: props.leafLabels ? 26 : 14,
}))
const tree = computed(() => dendrogram(props.Z))
const top = computed(() => props.yMax ?? (tree.value.maxHeight * 1.05 || 1))
const xMax = computed(() => 10 * (props.Z.length + 1))
const tx = (v: number) => pad.value.l + (v / xMax.value) * (W - pad.value.l - pad.value.r)
const ty = (v: number) =>
  pad.value.t + (1 - v / top.value) * (H - pad.value.t - pad.value.b)

const paths = computed(() =>
  tree.value.links.map((l) => ({
    d: `M${tx(l.x[0]).toFixed(1)},${ty(l.y[0]).toFixed(1)} L${tx(l.x[1]).toFixed(1)},${ty(
      l.y[1],
    ).toFixed(1)} L${tx(l.x[2]).toFixed(1)},${ty(l.y[2]).toFixed(1)} L${tx(l.x[3]).toFixed(
      1,
    )},${ty(l.y[3]).toFixed(1)}`,
    color: props.colorOf ? props.colorOf(l.id, l.height) : INK,
  })),
)
const ticks = computed(() => {
  if (props.yTicks) return props.yTicks
  const step = niceStep(top.value / 4)
  const out: number[] = []
  for (let v = 0; v <= top.value * 1.0001; v += step) out.push(Number(v.toFixed(6)))
  return out
})
function niceStep(raw: number): number {
  const mag = 10 ** Math.floor(Math.log10(raw))
  const n = raw / mag
  return (n < 1.5 ? 1 : n < 3 ? 2 : n < 7 ? 5 : 10) * mag
}
</script>

<template>
  <figure class="chart">
    <figcaption v-if="title" :style="{ color: titleColor }" v-html="title" />
    <svg :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none">
      <line
        :x1="pad.l" :x2="pad.l" :y1="pad.t" :y2="H - pad.b"
        :style="{ stroke: INK, strokeWidth: 1.1 }"
      />
      <template v-for="(t, i) in ticks" :key="`t${i}`">
        <line
          :x1="pad.l - 4" :x2="pad.l" :y1="ty(t)" :y2="ty(t)"
          :style="{ stroke: INK, strokeWidth: 1 }"
        />
        <text :x="pad.l - 7" :y="ty(t) + 4" class="tick end">{{ t }}</text>
      </template>
      <path
        v-for="(p, i) in paths" :key="`p${i}`"
        :d="p.d"
        :style="{ fill: 'none', stroke: p.color, strokeWidth: width, strokeLinejoin: 'round' }"
      />
      <template v-for="(c, i) in cuts" :key="`c${i}`">
        <line
          :x1="pad.l" :x2="W - pad.r" :y1="ty(c.y)" :y2="ty(c.y)"
          :style="{ stroke: c.color || '#c53030', strokeWidth: 1.8, strokeDasharray: c.dash || '6,4' }"
        />
        <text
          v-if="c.label" :x="W - pad.r - 2" :y="ty(c.y) - 4"
          :style="{ fill: c.color || '#c53030', fontSize: '11px', textAnchor: 'end' }"
        >{{ c.label }}</text>
      </template>
      <template v-if="leafLabels">
        <text
          v-for="(leaf, i) in tree.leaves" :key="`l${i}`"
          :x="tx(5 + 10 * i)" :y="H - pad.b + 13"
          class="tick mid"
        >{{ leafLabels[leaf] }}</text>
      </template>
      <text
        v-if="yLabel" :transform="`translate(11, ${(pad.t + H - pad.b) / 2}) rotate(-90)`"
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
