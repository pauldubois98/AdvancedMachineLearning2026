<!-- An SVG chart for the 1D pictures: loss curves, kernel profiles, the
     epsilon-tube, scaling laws. Axes are drawn only where the deck draws them. -->
<script setup lang="ts">
// NOTE: never use a bare `opacity` attribute here. Slidev runs UnoCSS with
// attributify, which rewrites opacity="1" into the utility class opacity-1,
// i.e. 1% opacity, and the curve all but disappears. stroke-opacity and
// fill-opacity are not utility names, so they survive.
import { computed } from 'vue'
import { GRID, INK, MUTED } from '../lib/theme'

export interface Series {
  points: [number, number][]
  color?: string
  width?: number
  dash?: string
  /** draw as a step function (the 0/1 loss) */
  step?: boolean
  opacity?: number
}

const props = withDefaults(
  defineProps<{
    series: Series[]
    /** shaded vertical band(s), in data coordinates */
    bands?: { x0: number; x1: number; color?: string; alpha?: number }[]
    /** shaded region between two curves */
    ribbons?: { points: [number, number, number][]; color?: string; alpha?: number }[]
    dots?: { x: number; y: number; color?: string; r?: number; hollow?: boolean; marker?: 'circle' | 'triangle' }[]
    vlines?: { x: number; color?: string; dash?: string; label?: string }[]
    hlines?: { y: number; color?: string; dash?: string }[]
    labels?: { x: number; y: number; text: string; color?: string; size?: number; anchor?: string }[]
    xDomain: [number, number]
    yDomain: [number, number]
    xLabel?: string
    yLabel?: string
    xTicks?: number[]
    yTicks?: number[]
    logX?: boolean
    logY?: boolean
    axes?: boolean
    title?: string
    titleColor?: string
    pad?: { l: number; r: number; t: number; b: number }
  }>(),
  {
    bands: () => [], ribbons: () => [], dots: () => [], vlines: () => [],
    hlines: () => [], labels: () => [], xLabel: '', yLabel: '', axes: true,
    logX: false, logY: false, title: '', titleColor: INK,
    pad: () => ({ l: 46, r: 14, t: 10, b: 34 }),
  },
)

const W = 600
const H = 320
// curves are clipped to the plot box, the way matplotlib's axes limits clip
const clipId = `lc-clip-${Math.random().toString(36).slice(2, 9)}`
const inner = computed(() => ({
  w: W - props.pad.l - props.pad.r,
  h: H - props.pad.t - props.pad.b,
}))
const tx = (v: number) => {
  const [a, b] = props.xDomain
  const f = props.logX
    ? (Math.log10(v) - Math.log10(a)) / (Math.log10(b) - Math.log10(a))
    : (v - a) / (b - a)
  return props.pad.l + f * inner.value.w
}
const ty = (v: number) => {
  const [a, b] = props.yDomain
  const f = props.logY
    ? (Math.log10(v) - Math.log10(a)) / (Math.log10(b) - Math.log10(a))
    : (v - a) / (b - a)
  return props.pad.t + (1 - f) * inner.value.h
}

function path(s: Series): string {
  if (!s.points.length) return ''
  const parts: string[] = []
  s.points.forEach(([x, y], i) => {
    const X = tx(x)
    const Y = ty(y)
    if (i === 0) parts.push(`M${X.toFixed(2)},${Y.toFixed(2)}`)
    else if (s.step) {
      const prev = s.points[i - 1]
      parts.push(`L${X.toFixed(2)},${ty(prev[1]).toFixed(2)}`, `L${X.toFixed(2)},${Y.toFixed(2)}`)
    } else parts.push(`L${X.toFixed(2)},${Y.toFixed(2)}`)
  })
  return parts.join(' ')
}

function ribbon(r: { points: [number, number, number][] }): string {
  const up = r.points.map(([x, lo, hi]) => `${tx(x).toFixed(2)},${ty(hi).toFixed(2)}`)
  const down = [...r.points].reverse().map(([x, lo]) => `${tx(x).toFixed(2)},${ty(lo).toFixed(2)}`)
  return `M${up.join(' L')} L${down.join(' L')} Z`
}

const paths = computed(() => props.series.map((s) => ({ d: path(s), s })))
</script>

<template>
  <figure class="chart">
    <figcaption v-if="title" :style="{ color: titleColor }" v-html="title" />
    <svg :viewBox="`0 0 ${W} ${H}`" preserveAspectRatio="none">
      <defs>
        <clipPath :id="clipId">
          <rect :x="pad.l" :y="0" :width="inner.w" :height="pad.t + inner.h" />
        </clipPath>
      </defs>
      <g :clip-path="`url(#${clipId})`">
      <rect
        v-for="(b, i) in bands" :key="`b${i}`"
        :x="tx(b.x0)" :y="pad.t" :width="Math.max(0, tx(b.x1) - tx(b.x0))" :height="inner.h"
        :style="{ fill: b.color || '#00ab0e', fillOpacity: b.alpha ?? 0.1 }"
      />
      <path
        v-for="(r, i) in ribbons" :key="`r${i}`"
        :d="ribbon(r)"
        :style="{ fill: r.color || '#00ab0e', fillOpacity: r.alpha ?? 0.16 }"
      />
      <line
        v-for="(l, i) in hlines" :key="`h${i}`"
        :x1="pad.l" :x2="W - pad.r" :y1="ty(l.y)" :y2="ty(l.y)"
        :style="{ stroke: l.color || GRID, strokeWidth: 1.2, strokeDasharray: l.dash || 'none' }"
      />
      <line
        v-for="(l, i) in vlines" :key="`v${i}`"
        :x1="tx(l.x)" :x2="tx(l.x)" :y1="pad.t" :y2="pad.t + inner.h"
        :style="{ stroke: l.color || GRID, strokeWidth: 1.2, strokeDasharray: (l.dash ?? '2,3') || 'none' }"
      />
      </g>
      <!-- axes -->
      <template v-if="axes">
        <line
          :x1="pad.l" :x2="pad.l" :y1="pad.t" :y2="pad.t + inner.h"
          :style="{ stroke: INK, strokeWidth: 1.1 }"
        />
        <line
          :x1="pad.l" :x2="W - pad.r" :y1="pad.t + inner.h" :y2="pad.t + inner.h"
          :style="{ stroke: INK, strokeWidth: 1.1 }"
        />
        <template v-for="(t, i) in xTicks || []" :key="`xt${i}`">
          <line
            :x1="tx(t)" :x2="tx(t)" :y1="pad.t + inner.h" :y2="pad.t + inner.h + 4"
            :style="{ stroke: INK, strokeWidth: 1 }"
          />
          <text :x="tx(t)" :y="pad.t + inner.h + 16" class="tick mid">{{ t }}</text>
        </template>
        <template v-for="(t, i) in yTicks || []" :key="`yt${i}`">
          <line
            :x1="pad.l - 4" :x2="pad.l" :y1="ty(t)" :y2="ty(t)"
            :style="{ stroke: INK, strokeWidth: 1 }"
          />
          <text :x="pad.l - 7" :y="ty(t) + 4" class="tick end">{{ t }}</text>
        </template>
      </template>
      <g :clip-path="`url(#${clipId})`">
      <path
        v-for="(p, i) in paths" :key="`p${i}`"
        :d="p.d"
        :style="{
          fill: 'none',
          stroke: p.s.color || INK,
          strokeWidth: p.s.width ?? 2.4,
          strokeDasharray: p.s.dash || 'none',
          strokeOpacity: p.s.opacity ?? 1,
          strokeLinejoin: 'round',
          strokeLinecap: 'round',
        }"
      />
      </g>
      <template v-for="(d, i) in dots" :key="`d${i}`">
        <polygon
          v-if="d.marker === 'triangle'"
          :points="`${tx(d.x)},${ty(d.y) - (d.r ?? 4) * 1.15} ${tx(d.x) + (d.r ?? 4) * 1.1},${ty(d.y) + (d.r ?? 4) * 0.8} ${tx(d.x) - (d.r ?? 4) * 1.1},${ty(d.y) + (d.r ?? 4) * 0.8}`"
          :style="{
            fill: d.hollow ? 'none' : d.color || INK,
            stroke: d.color || INK,
            strokeWidth: 1.8,
          }"
        />
        <circle
          v-else
          :cx="tx(d.x)" :cy="ty(d.y)" :r="d.r ?? 4"
          :style="{
            fill: d.hollow ? '#fff' : d.color || INK,
            stroke: d.color || INK,
            strokeWidth: d.hollow ? 1.8 : 0,
          }"
        />
      </template>
      <text
        v-for="(l, i) in labels" :key="`l${i}`"
        :x="tx(l.x)" :y="ty(l.y)"
        :style="{ fill: l.color || INK, fontSize: `${l.size ?? 13}px`, textAnchor: l.anchor || 'start' }"
      >{{ l.text }}</text>
      <text v-if="xLabel" :x="pad.l + inner.w / 2" :y="H - 4" class="axis-label mid">{{ xLabel }}</text>
      <text
        v-if="yLabel" :transform="`translate(11, ${pad.t + inner.h / 2}) rotate(-90)`"
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
