<!-- A matrix drawn as a heatmap of cells, the way the printed figures draw X,
     W and H: white is zero, one ramp per matrix. Optionally a mask (missing
     cells in light grey) and a highlighted column or row. -->
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type { Mat } from '../lib/mat'
import { LIGHT, RAMPS, type RampName } from '../lib/theme'

const props = withDefaults(
  defineProps<{
    M: Mat
    ramp?: RampName
    vmin?: number
    vmax?: number | null
    mask?: Mat | null
    border?: string
    title?: string
    titleColor?: string
    caption?: string
    /** outline one column (or one row) */
    hiCol?: number | null
    hiRow?: number | null
    /** draw row 0 at the bottom, as an image with origin="lower" */
    flip?: boolean
    /** keep the cells square, centred in the box */
    square?: boolean
    /** a signed matrix on the diverging ramp: symmetric limits */
    signed?: boolean
  }>(),
  {
    ramp: 'x', vmin: 0, vmax: null, mask: null, border: '', title: '', titleColor: '#1b1b1b',
    caption: '', hiCol: null, hiRow: null, flip: false, square: false, signed: false,
  },
)

const canvas = ref<HTMLCanvasElement | null>(null)
let ro: ResizeObserver | null = null

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth || !el.clientHeight) return
  const dpr = window.devicePixelRatio || 1
  el.width = Math.round(el.clientWidth * dpr)
  el.height = Math.round(el.clientHeight * dpr)
  const ctx = el.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  ctx.clearRect(0, 0, el.clientWidth, el.clientHeight)
  const { M } = props
  let bw = el.clientWidth
  let bh = el.clientHeight
  let ox = 0
  let oy = 0
  if (props.square) {
    const s = Math.min(bw / M.c, bh / M.r)
    ox = (bw - s * M.c) / 2
    oy = (bh - s * M.r) / 2
    bw = s * M.c
    bh = s * M.r
  }
  // paint the cells into an offscreen image, then scale it up unsmoothed
  const off = document.createElement('canvas')
  off.width = M.c
  off.height = M.r
  const octx = off.getContext('2d')!
  const img = octx.createImageData(M.c, M.r)
  let lo = props.vmin
  let hi = props.vmax ?? -Infinity
  if (props.vmax == null) for (const v of M.a) if (v > hi) hi = v
  if (props.signed) {
    let m = 0
    for (const v of M.a) m = Math.max(m, Math.abs(v))
    lo = -m
    hi = m
  }
  const ramp = RAMPS[props.ramp]
  const grey = [0xed, 0xee, 0xf0]
  for (let i = 0; i < M.r; i++) {
    const di = props.flip ? M.r - 1 - i : i
    for (let j = 0; j < M.c; j++) {
      const k = (di * M.c + j) * 4
      const missing = props.mask && props.mask.a[i * M.c + j] === 0
      const [r, g, b] = missing ? grey : ramp((M.a[i * M.c + j] - lo) / (hi - lo || 1))
      img.data[k] = r
      img.data[k + 1] = g
      img.data[k + 2] = b
      img.data[k + 3] = 255
    }
  }
  octx.putImageData(img, 0, 0)
  ctx.imageSmoothingEnabled = false
  ctx.drawImage(off, ox, oy, bw, bh)
  if (props.border) {
    ctx.strokeStyle = props.border
    ctx.lineWidth = 2
    ctx.strokeRect(ox + 1, oy + 1, bw - 2, bh - 2)
  }
  ctx.strokeStyle = '#1b1b1b'
  ctx.lineWidth = 1.6
  if (props.hiCol != null) {
    const cw = bw / M.c
    ctx.strokeRect(ox + props.hiCol * cw, oy + 0.8, cw, bh - 1.6)
  }
  if (props.hiRow != null) {
    const rh = bh / M.r
    const rr = props.flip ? M.r - 1 - props.hiRow : props.hiRow
    ctx.strokeRect(ox + 0.8, oy + rr * rh, bw - 1.6, rh)
  }
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
watch(() => [props.M, props.M.a, props.mask, props.hiCol, props.hiRow, props.vmax, props.ramp], schedule)
defineExpose({ draw: schedule })
void LIGHT
</script>

<template>
  <figure class="mat">
    <figcaption v-if="title" :style="{ color: titleColor }" v-html="title" />
    <canvas ref="canvas" />
    <div v-if="caption" class="cap" v-html="caption" />
  </figure>
</template>

<style scoped>
.mat { display: flex; flex-direction: column; margin: 0; min-height: 0; height: 100%; }
figcaption { text-align: center; font-size: 0.82rem; font-weight: 600; margin-bottom: 0.2rem; }
canvas { flex: 1 1 0; min-height: 0; width: 100%; display: block; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.72rem; margin-top: 0.2rem; line-height: 1.35; }
</style>
