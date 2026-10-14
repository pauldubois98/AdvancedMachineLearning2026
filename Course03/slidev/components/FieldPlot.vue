<!-- The 2D panel every classifier slide uses: shaded decision field, the
     street at f = -1, 0, +1, the class markers, and whatever rings or
     straight lines the slide needs on top. -->
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import {
  Domain, contour, dataDomain, drawBand, drawLine, drawPoints, equalise,
  frame, paintField, paintRegions, ringPoints, sampleField, strokePath,
} from '../lib/plot'
import { GREEN, INK, MUTED, RED, BLUE } from '../lib/theme'

const props = withDefaults(
  defineProps<{
    X: number[][]
    y: number[]
    /** f(x1, x2); when absent only the points are drawn */
    decision?: ((x: number, y: number) => number) | null
    /** an already-sampled field, for panels that cache it between frames */
    grid?: Float64Array | Float32Array | null
    gridRes?: number
    /** further decision functions, drawn as thin boundaries only: the tree
     *  boundaries a forest is about to average */
    extraContours?: ((x: number, y: number) => number)[]
    /** flat class map instead of the shaded field (multiclass slides) */
    regions?: ((x: number, y: number) => number) | null
    regionColors?: readonly string[]
    /** indices to circle, e.g. the support vectors */
    rings?: { idx: number[]; color?: string; size?: number; width?: number }[]
    /** straight segments in data coordinates: the cuts of a tree partition */
    segments?: { from: [number, number]; to: [number, number]; color?: string; width?: number; dash?: number[] }[]
    /** filled rectangles under everything else: the leaves of a tree */
    boxes?: { x0: number; x1: number; y0: number; y1: number; color: string; alpha?: number }[]
    /** straight lines y = a x + c */
    lines?: { a: number; c: number; color?: string; width?: number; dash?: number[] }[]
    /** a shaded street around a straight line */
    band?: { a: number; c: number; half: number; color?: string; alpha?: number } | null
    /** arrows in data coordinates */
    arrows?: { from: [number, number]; to: [number, number]; color?: string }[]
    domain?: Domain | null
    margins?: boolean
    boundary?: boolean
    aspect?: 'equal' | 'auto'
    res?: number
    pointSize?: number
    pointAlpha?: number
    fieldAlpha?: number
    palette?: readonly string[]
    pad?: number
    /** a highlighted test point, drawn as a hollow ink ring */
    probe?: [number, number] | null
    title?: string
    titleColor?: string
  }>(),
  {
    decision: null, grid: null, gridRes: 0, regions: null, rings: () => [], lines: () => [], band: null,
    segments: () => [], boxes: () => [], extraContours: () => [],
    arrows: () => [], domain: null, margins: true, boundary: true, aspect: 'equal',
    res: 130, pointSize: 22, pointAlpha: 1, fieldAlpha: 0.7, pad: 0.7,
    regionColors: () => ['#dce7f2', '#f6dcdc', '#d9efdb'], probe: null,
    palette: () => [BLUE, RED, GREEN], title: '', titleColor: INK,
  },
)

const emit = defineEmits<{ pick: [[number, number]] }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let lastFrame: ReturnType<typeof frame> | null = null

function onClick(ev: MouseEvent) {
  const el = canvas.value
  if (!el || !lastFrame) return
  const r = el.getBoundingClientRect()
  const [x0, x1, y0, y1] = lastFrame.d
  const x = x0 + ((ev.clientX - r.left) / r.width) * (x1 - x0)
  const y = y0 + (1 - (ev.clientY - r.top) / r.height) * (y1 - y0)
  emit('pick', [x, y])
}
let queued = 0

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth) return
  let d = props.domain ?? dataDomain(props.X, props.pad)
  if (props.aspect === 'equal') d = equalise(d, el.clientWidth, el.clientHeight)
  const fr = frame(el, d)
  lastFrame = fr

  for (const b of props.boxes) {
    const { ctx } = fr
    ctx.save()
    ctx.globalAlpha = b.alpha ?? 1
    ctx.fillStyle = b.color
    ctx.fillRect(fr.sx(b.x0), fr.sy(b.y1), fr.sx(b.x1) - fr.sx(b.x0), fr.sy(b.y0) - fr.sy(b.y1))
    ctx.restore()
  }

  if (props.regions) {
    const res = Math.min(props.res, 160)
    const [x0, x1, y0, y1] = d
    const labels = new Int32Array(res * res)
    for (let j = 0; j < res; j++) {
      const yy = y0 + ((y1 - y0) * j) / (res - 1)
      for (let i = 0; i < res; i++)
        labels[j * res + i] = props.regions(x0 + ((x1 - x0) * i) / (res - 1), yy)
    }
    paintRegions(fr, labels, res, props.regionColors)
  } else if (props.grid || props.decision) {
    const res = props.grid ? props.gridRes : props.res
    const g = props.grid
      ? (props.grid instanceof Float64Array ? props.grid : Float64Array.from(props.grid))
      : sampleField(props.decision!, d, res)
    paintField(fr, g, res, props.fieldAlpha)
    if (props.boundary) strokePath(fr, contour(g, res, 0, d), INK, 1.8)
    if (props.margins) {
      strokePath(fr, contour(g, res, -1, d), INK, 1.1, [5, 4])
      strokePath(fr, contour(g, res, 1, d), INK, 1.1, [5, 4])
    }
  }

  for (const f of props.extraContours) {
    const res = Math.min(props.res, 110)
    strokePath(fr, contour(sampleField(f, d, res), res, 0, d), MUTED, 1, [])
  }

  if (props.band)
    drawBand(fr, props.band.a, props.band.c, props.band.half,
      props.band.color ?? '#b7791f', props.band.alpha ?? 0.3)
  for (const l of props.lines)
    drawLine(fr, l.a, l.c, l.color ?? INK, l.width ?? 2, l.dash ?? [])
  for (const s of props.segments)
    strokePath(fr, [[s.from, s.to]], s.color ?? INK, s.width ?? 2, s.dash ?? [])

  drawPoints(fr, props.X, props.y, props.pointSize, props.pointAlpha, props.palette)
  for (const r of props.rings)
    ringPoints(fr, props.X, r.idx, r.color ?? GREEN, r.size ?? 140, r.width ?? 2)

  const { ctx } = fr
  if (props.probe) {
    const px = fr.sx(props.probe[0])
    const py = fr.sy(props.probe[1])
    ctx.save()
    ctx.strokeStyle = INK
    ctx.lineWidth = 2.2
    ctx.beginPath()
    ctx.arc(px, py, 7, 0, 2 * Math.PI)
    ctx.stroke()
    ctx.beginPath()
    ctx.moveTo(px - 11, py)
    ctx.lineTo(px + 11, py)
    ctx.moveTo(px, py - 11)
    ctx.lineTo(px, py + 11)
    ctx.lineWidth = 1
    ctx.stroke()
    ctx.restore()
  }
  for (const a of props.arrows) {
    const x1 = fr.sx(a.from[0]), y1 = fr.sy(a.from[1])
    const x2 = fr.sx(a.to[0]), y2 = fr.sy(a.to[1])
    ctx.save()
    ctx.strokeStyle = a.color ?? '#b7791f'
    ctx.fillStyle = a.color ?? '#b7791f'
    ctx.lineWidth = 1.8
    ctx.beginPath()
    ctx.moveTo(x1, y1)
    ctx.lineTo(x2, y2)
    ctx.stroke()
    const ang = Math.atan2(y2 - y1, x2 - x1)
    ctx.beginPath()
    ctx.moveTo(x2, y2)
    ctx.lineTo(x2 - 7 * Math.cos(ang - 0.4), y2 - 7 * Math.sin(ang - 0.4))
    ctx.lineTo(x2 - 7 * Math.cos(ang + 0.4), y2 - 7 * Math.sin(ang + 0.4))
    ctx.closePath()
    ctx.fill()
    ctx.restore()
  }
}

function schedule() {
  if (queued) return
  queued = requestAnimationFrame(() => {
    queued = 0
    draw()
  })
}

let ro: ResizeObserver | null = null
onMounted(() => {
  draw()
  ro = new ResizeObserver(schedule)
  if (canvas.value) ro.observe(canvas.value)
})
onBeforeUnmount(() => ro?.disconnect())
watch(() => props, schedule, { deep: true })
</script>

<template>
  <figure class="field">
    <figcaption v-if="title" :style="{ color: titleColor }">{{ title }}</figcaption>
    <canvas ref="canvas" @click="onClick" />
  </figure>
</template>

<style scoped>
.field { display: flex; flex-direction: column; height: 100%; min-height: 0; margin: 0; }
figcaption { text-align: center; font-size: 0.82rem; font-weight: 600; margin-bottom: 0.2rem; }
canvas { width: 100%; flex: 1 1 0; min-height: 0; display: block; }
</style>
