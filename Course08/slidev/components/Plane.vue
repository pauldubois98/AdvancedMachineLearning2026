<!-- The 2-D pictures: a cloud of points, the level sets of the components
     (ellipses at one and two standard deviations), and optionally a shaded
     field and its contours. Data aspect is kept square, as matplotlib's
     set_aspect("equal") does. Clicks are reported in data coordinates. -->
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { contour, equalise, frame, sampleField, strokePath, type Domain, type Frame } from '../lib/plot'
import { ellipseAxes, type Cov, type Pt } from '../lib/gmm'
import { INK } from '../lib/theme'

export interface Ell { mu: Pt; S: Cov; color: string; nsig?: number[]; width?: number; dash?: number[] }
export interface Marker { at: Pt; color: string; shape?: 'x' | 'star' | 'dot' | 'ring'; size?: number }
export interface Level { f: (x: number, y: number) => number; level: number; color: string; width?: number; dash?: number[] }

const props = withDefaults(
  defineProps<{
    X?: Pt[]
    colors?: string[] | string
    size?: number
    alpha?: number
    ellipses?: Ell[]
    markers?: Marker[]
    /** a shaded field: value -> rgb */
    field?: ((x: number, y: number) => number) | null
    fieldColor?: (v: number) => [number, number, number]
    fieldRes?: number
    levels?: Level[]
    domain: Domain
    equal?: boolean
    axes?: boolean
    xLabel?: string
    yLabel?: string
    title?: string
    titleColor?: string
    caption?: string
    pickable?: boolean
  }>(),
  {
    X: () => [], colors: INK, size: 3, alpha: 0.85, ellipses: () => [], markers: () => [],
    field: null, fieldRes: 120, levels: () => [], equal: true, axes: false,
    xLabel: '', yLabel: '', title: '', titleColor: INK, caption: '', pickable: false,
  },
)
const emit = defineEmits<{ pick: [x: number, y: number] }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let fr: Frame | null = null
let ro: ResizeObserver | null = null
const PAD = { l: 0, b: 0 }

function niceStep(span: number): number {
  const raw = span / 5
  const p = 10 ** Math.floor(Math.log10(raw))
  return [1, 2, 5, 10].map((m) => m * p).find((s) => s >= raw) ?? raw
}

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth || !el.clientHeight) return
  const padL = props.axes ? 38 : 0
  const padB = props.axes ? 30 : 0
  PAD.l = padL
  PAD.b = padB
  const w = el.clientWidth - padL - (props.axes ? 12 : 0)
  const h = el.clientHeight - padB
  const d = props.equal ? equalise(props.domain, w, h) : props.domain
  fr = frame(el, d)
  const [x0, x1, y0, y1] = d
  // the plot box sits right of / above the axes
  const sx = (v: number) => padL + ((v - x0) / (x1 - x0)) * w
  const sy = (v: number) => h - ((v - y0) / (y1 - y0)) * h
  fr.sx = sx
  fr.sy = sy
  const { ctx } = fr

  if (props.field && props.fieldColor) {
    const res = props.fieldRes
    const g = sampleField(props.field, d, res)
    const off = document.createElement('canvas')
    off.width = res
    off.height = res
    const octx = off.getContext('2d')!
    const img = octx.createImageData(res, res)
    for (let j = 0; j < res; j++) for (let i = 0; i < res; i++) {
      const [r, gg, b] = props.fieldColor(g[j * res + i])
      const k = ((res - 1 - j) * res + i) * 4
      img.data[k] = r; img.data[k + 1] = gg; img.data[k + 2] = b; img.data[k + 3] = 255
    }
    octx.putImageData(img, 0, 0)
    ctx.save()
    ctx.imageSmoothingEnabled = true
    ctx.drawImage(off, padL, 0, w, h)
    ctx.restore()
  }
  for (const L of props.levels) {
    const res = 140
    const g = sampleField(L.f, d, res)
    strokePath(fr, contour(g, res, L.level, d), L.color, L.width ?? 1.8, L.dash ?? [])
  }

  // points
  const cols = props.colors
  const r = props.size
  ctx.save()
  ctx.globalAlpha = props.alpha
  props.X.forEach((p, i) => {
    ctx.fillStyle = typeof cols === 'string' ? cols : cols[i] ?? INK
    ctx.beginPath()
    ctx.arc(sx(p[0]), sy(p[1]), r, 0, 2 * Math.PI)
    ctx.fill()
  })
  ctx.restore()

  // ellipses, in data units: the transform maps data to pixels
  const ux = w / (x1 - x0)
  const uy = h / (y1 - y0)
  for (const e of props.ellipses) {
    const { r1, r2, angle } = ellipseAxes(e.S)
    for (const k of e.nsig ?? [1, 2]) {
      ctx.save()
      ctx.strokeStyle = e.color
      ctx.lineWidth = e.width ?? 1.6
      ctx.setLineDash(e.dash ?? [])
      ctx.beginPath()
      for (let s = 0; s <= 72; s++) {
        const th = (2 * Math.PI * s) / 72
        const ex = k * r1 * Math.cos(th)
        const ey = k * r2 * Math.sin(th)
        const X = e.mu[0] + ex * Math.cos(angle) - ey * Math.sin(angle)
        const Y = e.mu[1] + ex * Math.sin(angle) + ey * Math.cos(angle)
        const px = padL + (X - x0) * ux
        const py = h - (Y - y0) * uy
        if (s === 0) ctx.moveTo(px, py)
        else ctx.lineTo(px, py)
      }
      ctx.stroke()
      ctx.restore()
    }
  }

  for (const m of props.markers) {
    const px = sx(m.at[0])
    const py = sy(m.at[1])
    const s = m.size ?? 6
    ctx.save()
    ctx.strokeStyle = m.color
    ctx.fillStyle = m.color
    ctx.lineWidth = 2.2
    ctx.beginPath()
    if (m.shape === 'x') {
      ctx.moveTo(px - s, py - s); ctx.lineTo(px + s, py + s)
      ctx.moveTo(px + s, py - s); ctx.lineTo(px - s, py + s)
      ctx.stroke()
    } else if (m.shape === 'star') {
      for (let q = 0; q < 10; q++) {
        const rr = q % 2 ? s * 0.45 : s
        const a = -Math.PI / 2 + (q * Math.PI) / 5
        if (q === 0) ctx.moveTo(px + rr * Math.cos(a), py + rr * Math.sin(a))
        else ctx.lineTo(px + rr * Math.cos(a), py + rr * Math.sin(a))
      }
      ctx.closePath()
      ctx.fill()
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 0.8
      ctx.stroke()
    } else if (m.shape === 'ring') {
      ctx.arc(px, py, s, 0, 2 * Math.PI)
      ctx.stroke()
    } else {
      ctx.arc(px, py, s, 0, 2 * Math.PI)
      ctx.fill()
    }
    ctx.restore()
  }

  if (props.axes) {
    ctx.save()
    ctx.strokeStyle = INK
    ctx.fillStyle = INK
    ctx.lineWidth = 1
    ctx.font = '11px Lato, sans-serif'
    ctx.beginPath()
    ctx.moveTo(padL, 0); ctx.lineTo(padL, h); ctx.lineTo(padL + w, h)
    ctx.stroke()
    const stx = niceStep(x1 - x0)
    ctx.textAlign = 'center'
    for (let v = Math.ceil(x0 / stx) * stx; v <= x1; v += stx) {
      ctx.beginPath(); ctx.moveTo(sx(v), h); ctx.lineTo(sx(v), h + 4); ctx.stroke()
      ctx.fillText(String(+v.toPrecision(6)), sx(v), h + 15)
    }
    const sty = niceStep(y1 - y0)
    ctx.textAlign = 'right'
    for (let v = Math.ceil(y0 / sty) * sty; v <= y1; v += sty) {
      ctx.beginPath(); ctx.moveTo(padL - 4, sy(v)); ctx.lineTo(padL, sy(v)); ctx.stroke()
      ctx.fillText(String(+v.toPrecision(6)), padL - 6, sy(v) + 4)
    }
    ctx.font = '12px Lato, sans-serif'
    ctx.textAlign = 'center'
    if (props.xLabel) ctx.fillText(props.xLabel, padL + w / 2, h + 28)
    if (props.yLabel) {
      ctx.translate(10, h / 2)
      ctx.rotate(-Math.PI / 2)
      ctx.fillText(props.yLabel, 0, 0)
    }
    ctx.restore()
  }
}

function onClick(e: MouseEvent) {
  const el = canvas.value
  if (!el || !fr || !props.pickable) return
  const r = el.getBoundingClientRect()
  const fx = ((e.clientX - r.left) * el.clientWidth) / r.width
  const fy = ((e.clientY - r.top) * el.clientHeight) / r.height
  const [x0, x1, y0, y1] = fr.d
  const w = el.clientWidth - PAD.l - (props.axes ? 12 : 0)
  const h = el.clientHeight - PAD.b
  emit('pick', x0 + ((fx - PAD.l) / w) * (x1 - x0), y0 + ((h - fy) / h) * (y1 - y0))
}

let queued = 0
function schedule() {
  if (queued) return
  queued = requestAnimationFrame(() => { queued = 0; draw() })
}
onMounted(() => {
  draw()
  ro = new ResizeObserver(schedule)
  if (canvas.value) ro.observe(canvas.value)
})
onBeforeUnmount(() => ro?.disconnect())
watch(() => [props.X, props.colors, props.ellipses, props.markers, props.field, props.levels, props.domain, props.size], schedule)
</script>

<template>
  <figure class="plane">
    <figcaption v-if="title" :style="{ color: titleColor }" v-html="title" />
    <canvas ref="canvas" :class="{ pickable }" @click="onClick" />
    <div v-if="caption" class="cap" v-html="caption" />
  </figure>
</template>

<style scoped>
.plane { display: flex; flex-direction: column; margin: 0; min-height: 0; height: 100%; }
figcaption { text-align: center; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.2rem; }
canvas { flex: 1 1 0; min-height: 0; width: 100%; display: block; }
.pickable { cursor: crosshair; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; margin-top: 0.2rem; line-height: 1.35; }
</style>
