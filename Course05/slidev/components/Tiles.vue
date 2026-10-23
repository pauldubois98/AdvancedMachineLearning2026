<!-- Images in a grid, square tiles: faces, columns of W, PCA components.
     Each tile is scaled to its own range unless `vmax` is given. -->
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RAMPS, type RampName } from '../lib/theme'

const props = withDefaults(
  defineProps<{
    items: ArrayLike<number>[]
    side: number
    cols?: number
    ramp?: RampName
    vmin?: number | null
    vmax?: number | null
    /** diverging: symmetric limits, shared by all tiles */
    signed?: boolean
    gap?: number
    hi?: number | null
    hiColor?: string
    /** a thin outline around every tile, for images with a white background */
    frame?: string
    title?: string
    titleColor?: string
    caption?: string
  }>(),
  {
    cols: 0, ramp: 'gray', vmin: null, vmax: null, signed: false, gap: 3, hi: null,
    hiColor: '#1b1b1b', frame: '', title: '', titleColor: '#1b1b1b', caption: '',
  },
)

const canvas = ref<HTMLCanvasElement | null>(null)
let ro: ResizeObserver | null = null

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth || !el.clientHeight) return
  const n = props.items.length
  const W = el.clientWidth
  const H = el.clientHeight
  const g = props.gap
  // the largest square tile that fits n tiles in the box
  let cols = props.cols
  if (!cols) {
    let best = 1
    let bestS = 0
    for (let c = 1; c <= n; c++) {
      const rws = Math.ceil(n / c)
      const s = Math.min((W - g * (c - 1)) / c, (H - g * (rws - 1)) / rws)
      if (s > bestS) { bestS = s; best = c }
    }
    cols = best
  }
  const rws = Math.ceil(n / cols)
  const s = Math.floor(Math.min((W - g * (cols - 1)) / cols, (H - g * (rws - 1)) / rws))
  const ox = (W - (s * cols + g * (cols - 1))) / 2
  const oy = (H - (s * rws + g * (rws - 1))) / 2
  const dpr = window.devicePixelRatio || 1
  el.width = Math.round(W * dpr)
  el.height = Math.round(H * dpr)
  const ctx = el.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, W, H)
  const side = props.side
  const off = document.createElement('canvas')
  off.width = side
  off.height = side
  const octx = off.getContext('2d')!
  const ramp = RAMPS[props.ramp]
  let shared = 0
  if (props.signed) for (const it of props.items) for (let q = 0; q < it.length; q++) shared = Math.max(shared, Math.abs(it[q]))
  props.items.forEach((it, idx) => {
    let lo = props.vmin ?? Infinity
    let hi = props.vmax ?? -Infinity
    if (props.signed) { lo = -shared; hi = shared }
    else {
      if (props.vmin == null) for (let q = 0; q < it.length; q++) lo = Math.min(lo, it[q])
      if (props.vmax == null) for (let q = 0; q < it.length; q++) hi = Math.max(hi, it[q])
    }
    const img = octx.createImageData(side, side)
    for (let q = 0; q < side * side; q++) {
      const [r, gg, b] = ramp((it[q] - lo) / (hi - lo || 1))
      img.data[4 * q] = r
      img.data[4 * q + 1] = gg
      img.data[4 * q + 2] = b
      img.data[4 * q + 3] = 255
    }
    octx.putImageData(img, 0, 0)
    const x = ox + (idx % cols) * (s + g)
    const y = oy + Math.floor(idx / cols) * (s + g)
    ctx.imageSmoothingEnabled = s < side * 2
    ctx.drawImage(off, x, y, s, s)
    if (props.frame) {
      ctx.strokeStyle = props.frame
      ctx.lineWidth = 1
      ctx.strokeRect(x + 0.5, y + 0.5, s - 1, s - 1)
    }
    if (props.hi === idx) {
      ctx.strokeStyle = props.hiColor
      ctx.lineWidth = 2.2
      ctx.strokeRect(x - 1, y - 1, s + 2, s + 2)
    }
  })
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
watch(() => [props.items, props.hi, props.vmax, props.cols], schedule)
</script>

<template>
  <figure class="tiles">
    <figcaption v-if="title" :style="{ color: titleColor }" v-html="title" />
    <canvas ref="canvas" />
    <div v-if="caption" class="cap" v-html="caption" />
  </figure>
</template>

<style scoped>
.tiles { display: flex; flex-direction: column; margin: 0; min-height: 0; height: 100%; }
figcaption { text-align: center; font-size: 0.82rem; font-weight: 600; margin-bottom: 0.2rem; }
canvas { flex: 1 1 0; min-height: 0; width: 100%; display: block; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.72rem; margin-top: 0.2rem; line-height: 1.35; }
</style>
