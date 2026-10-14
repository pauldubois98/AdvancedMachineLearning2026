<!-- The 2D panel nearly every clustering slide uses: points coloured by
     cluster (noise stays grey), centre crosses, epsilon circles, the edges of
     a spanning tree, dashed group ellipses, and an optional density surface
     underneath. Drawn on a canvas, so a few hundred points redraw instantly. -->
<script setup lang="ts">
import { onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { Domain, dataDomain, equalise, frame } from '../lib/plot'
import { INK, MUTED, clusterColor, mountain as mountainRamp } from '../lib/theme'

export interface Circle { x: number; y: number; r: number; color?: string; alpha?: number; dash?: number[] }
export interface Edge { a: [number, number]; b: [number, number]; color?: string; width?: number; alpha?: number; dash?: number[] }
export interface Cross { x: number; y: number; color?: string; size?: number }
export interface Ell { x: number; y: number; rx: number; ry: number; angle?: number; color?: string; dash?: number[]; width?: number }
export interface Tag { x: number; y: number; text: string; color?: string; size?: number; anchor?: CanvasTextAlign; dy?: number }
export interface Field { f: (x: number, y: number) => number; vmax: number; vmin?: number; levels?: number; ramp?: (t: number) => [number, number, number]; res?: number }

const props = withDefaults(
  defineProps<{
    X: number[][]
    /** cluster per point, -1 for noise; absent means "one grey cloud" */
    labels?: number[] | null
    /** an explicit colour per point, which wins over `labels` */
    colors?: string[] | null
    /** an explicit radius per point, in pixels */
    sizes?: number[] | null
    pointSize?: number
    pointAlpha?: number
    noiseColor?: string
    /** draw the points at all: some panels only want the grid or the field */
    points?: boolean
    field?: Field | null
    circles?: Circle[]
    edges?: Edge[]
    crosses?: Cross[]
    ellipses?: Ell[]
    tags?: Tag[]
    /** faint candidate nodes, e.g. the mountain method's grid */
    grid?: number[][] | null
    /** spokes from each point to its centre: the inertia picture */
    spokes?: { from: [number, number]; to: [number, number]; color?: string; alpha?: number }[]
    domain?: Domain | null
    pad?: number
    aspect?: 'equal' | 'auto'
    title?: string
    titleColor?: string
  }>(),
  {
    labels: null, colors: null, sizes: null, pointSize: 3.2, pointAlpha: 0.85,
    noiseColor: MUTED, points: true, field: null, circles: () => [], edges: () => [],
    crosses: () => [], ellipses: () => [], tags: () => [], grid: null, spokes: () => [],
    domain: null, pad: 0.5, aspect: 'equal', title: '', titleColor: INK,
  },
)

const emit = defineEmits<{ pick: [[number, number]] }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let last: ReturnType<typeof frame> | null = null
let queued = 0

function onClick(ev: MouseEvent) {
  const el = canvas.value
  if (!el || !last) return
  const r = el.getBoundingClientRect()
  const [x0, x1, y0, y1] = last.d
  emit('pick', [
    x0 + ((ev.clientX - r.left) / r.width) * (x1 - x0),
    y0 + (1 - (ev.clientY - r.top) / r.height) * (y1 - y0),
  ])
}

function paintField(fr: ReturnType<typeof frame>, fld: Field) {
  const res = fld.res ?? 150
  const [x0, x1, y0, y1] = fr.d
  const ny = Math.max(20, Math.round((res * (y1 - y0)) / (x1 - x0)))
  const off = document.createElement('canvas')
  off.width = res
  off.height = ny
  const octx = off.getContext('2d')!
  const img = octx.createImageData(res, ny)
  const ramp = fld.ramp ?? mountainRamp
  const levels = fld.levels ?? 14
  const vmin = fld.vmin ?? 0
  for (let j = 0; j < ny; j++) {
    const yy = y0 + ((y1 - y0) * j) / (ny - 1)
    for (let i = 0; i < res; i++) {
      const v = fld.f(x0 + ((x1 - x0) * i) / (res - 1), yy)
      // contourf's bands: quantise before the colour lookup
      const t = Math.min(1, Math.max(0, (v - vmin) / (fld.vmax - vmin || 1)))
      const band = Math.min(levels - 1, Math.floor(t * levels)) / (levels - 1)
      const [r, g, b] = ramp(band)
      const k = ((ny - 1 - j) * res + i) * 4
      img.data[k] = r
      img.data[k + 1] = g
      img.data[k + 2] = b
      img.data[k + 3] = 255
    }
  }
  octx.putImageData(img, 0, 0)
  const { ctx } = fr
  ctx.save()
  ctx.imageSmoothingEnabled = false
  ctx.drawImage(off, 0, 0, fr.w, fr.h)
  ctx.restore()
}

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth || !props.X.length) return
  let d = props.domain ?? dataDomain(props.X, props.pad)
  if (props.aspect === 'equal') d = equalise(d, el.clientWidth, el.clientHeight)
  const fr = frame(el, d)
  last = fr
  const { ctx } = fr

  if (props.field) paintField(fr, props.field)

  if (props.grid) {
    ctx.save()
    ctx.fillStyle = '#cccfd2'
    for (const p of props.grid) {
      ctx.beginPath()
      ctx.arc(fr.sx(p[0]), fr.sy(p[1]), 1.1, 0, 2 * Math.PI)
      ctx.fill()
    }
    ctx.restore()
  }

  for (const s of props.spokes) {
    ctx.save()
    ctx.strokeStyle = s.color ?? '#2b6cb0'
    ctx.globalAlpha = s.alpha ?? 0.45
    ctx.lineWidth = 0.9
    ctx.beginPath()
    ctx.moveTo(fr.sx(s.from[0]), fr.sy(s.from[1]))
    ctx.lineTo(fr.sx(s.to[0]), fr.sy(s.to[1]))
    ctx.stroke()
    ctx.restore()
  }

  for (const e of props.edges) {
    ctx.save()
    ctx.strokeStyle = e.color ?? MUTED
    ctx.globalAlpha = e.alpha ?? 1
    ctx.lineWidth = e.width ?? 1.4
    ctx.setLineDash(e.dash ?? [])
    ctx.beginPath()
    ctx.moveTo(fr.sx(e.a[0]), fr.sy(e.a[1]))
    ctx.lineTo(fr.sx(e.b[0]), fr.sy(e.b[1]))
    ctx.stroke()
    ctx.restore()
  }

  for (const c of props.circles) {
    const rx = fr.sx(c.x + c.r) - fr.sx(c.x)
    ctx.save()
    ctx.beginPath()
    ctx.ellipse(fr.sx(c.x), fr.sy(c.y), Math.abs(rx), Math.abs(rx), 0, 0, 2 * Math.PI)
    ctx.fillStyle = c.color ?? '#00ab0e'
    ctx.globalAlpha = c.alpha ?? 0.12
    ctx.fill()
    ctx.globalAlpha = 1
    ctx.strokeStyle = c.color ?? '#00ab0e'
    ctx.lineWidth = 1.6
    ctx.setLineDash(c.dash ?? [])
    ctx.stroke()
    ctx.restore()
  }

  for (const e of props.ellipses) {
    const rx = Math.abs(fr.sx(e.x + e.rx) - fr.sx(e.x))
    const ry = Math.abs(fr.sy(e.y + e.ry) - fr.sy(e.y))
    ctx.save()
    ctx.strokeStyle = e.color ?? MUTED
    ctx.lineWidth = e.width ?? 1.6
    ctx.setLineDash(e.dash ?? [5, 4])
    ctx.beginPath()
    ctx.ellipse(fr.sx(e.x), fr.sy(e.y), rx, ry, -((e.angle ?? 0) * Math.PI) / 180, 0, 2 * Math.PI)
    ctx.stroke()
    ctx.restore()
  }

  if (props.points) {
    ctx.save()
    ctx.globalAlpha = props.pointAlpha
    props.X.forEach((p, i) => {
      const lab = props.labels ? props.labels[i] : 0
      const noise = !props.colors && props.labels != null && lab < 0
      ctx.fillStyle = props.colors
        ? props.colors[i]
        : props.labels
          ? noise ? props.noiseColor : clusterColor(lab)
          : INK
      const r = props.sizes ? props.sizes[i] : props.pointSize * (noise ? 0.78 : 1)
      ctx.beginPath()
      ctx.arc(fr.sx(p[0]), fr.sy(p[1]), r, 0, 2 * Math.PI)
      ctx.fill()
    })
    ctx.restore()
  }

  for (const c of props.crosses) {
    const px = fr.sx(c.x)
    const py = fr.sy(c.y)
    const s = c.size ?? 7
    ctx.save()
    ctx.strokeStyle = '#fff'
    ctx.lineWidth = 4.2
    ctx.lineCap = 'round'
    for (const [dx, dy] of [[1, 1], [1, -1]]) {
      ctx.beginPath()
      ctx.moveTo(px - s * dx, py - s * dy)
      ctx.lineTo(px + s * dx, py + s * dy)
      ctx.stroke()
    }
    ctx.strokeStyle = c.color ?? INK
    ctx.lineWidth = 2.6
    for (const [dx, dy] of [[1, 1], [1, -1]]) {
      ctx.beginPath()
      ctx.moveTo(px - s * dx, py - s * dy)
      ctx.lineTo(px + s * dx, py + s * dy)
      ctx.stroke()
    }
    ctx.restore()
  }

  for (const t of props.tags) {
    ctx.save()
    ctx.fillStyle = t.color ?? INK
    ctx.font = `${t.size ?? 12}px Lato, system-ui, sans-serif`
    ctx.textAlign = t.anchor ?? 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(t.text, fr.sx(t.x), fr.sy(t.y) + (t.dy ?? 0))
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
  <figure class="panel">
    <figcaption v-if="title" :style="{ color: titleColor }" v-html="title" />
    <canvas ref="canvas" @click="onClick" />
  </figure>
</template>

<style scoped>
.panel { display: flex; flex-direction: column; height: 100%; min-height: 0; margin: 0; }
figcaption { text-align: center; font-size: 0.82rem; font-weight: 600; margin-bottom: 0.15rem; line-height: 1.35; }
canvas { width: 100%; flex: 1 1 0; min-height: 0; display: block; }
</style>
