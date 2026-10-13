<!-- A generic contour panel: used for the Lagrangian's saddle. -->
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Domain, contour, frame, sampleField, strokePath } from '../lib/plot'
import { INK, rdbuR, rgb } from '../lib/theme'

const props = withDefaults(
  defineProps<{
    f: (x: number, y: number) => number
    domain: Domain
    /** value range the colours are stretched over */
    vmin: number
    vmax: number
    levels?: number[]
    res?: number
    marker?: [number, number] | null
    crosshair?: { x?: number; y?: number; xColor?: string; yColor?: string } | null
    xLabel?: string
    yLabel?: string
  }>(),
  { levels: () => [], res: 150, marker: null, crosshair: null, xLabel: '', yLabel: '' },
)

const canvas = ref<HTMLCanvasElement | null>(null)
let queued = 0

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth) return
  const fr = frame(el, props.domain)
  const g = sampleField(props.f, props.domain, props.res)
  const off = document.createElement('canvas')
  off.width = props.res
  off.height = props.res
  const octx = off.getContext('2d')!
  const img = octx.createImageData(props.res, props.res)
  for (let j = 0; j < props.res; j++) {
    for (let i = 0; i < props.res; i++) {
      const t = (g[j * props.res + i] - props.vmin) / (props.vmax - props.vmin)
      const [r, gg, b] = rdbuR(t)
      const k = ((props.res - 1 - j) * props.res + i) * 4
      img.data[k] = r
      img.data[k + 1] = gg
      img.data[k + 2] = b
      img.data[k + 3] = 255
    }
  }
  octx.putImageData(img, 0, 0)
  const { ctx } = fr
  ctx.save()
  ctx.globalAlpha = 0.9
  ctx.imageSmoothingEnabled = true
  ctx.drawImage(off, 0, 0, fr.w, fr.h)
  ctx.restore()

  for (const lv of props.levels)
    strokePath(fr, contour(g, props.res, lv, props.domain), 'rgba(27,27,27,0.45)', 1)

  if (props.crosshair) {
    const { x, y, xColor, yColor } = props.crosshair
    ctx.save()
    ctx.lineWidth = 1.6
    if (x !== undefined) {
      ctx.strokeStyle = xColor ?? INK
      ctx.beginPath()
      ctx.moveTo(fr.sx(x), 0)
      ctx.lineTo(fr.sx(x), fr.h)
      ctx.stroke()
    }
    if (y !== undefined) {
      ctx.strokeStyle = yColor ?? INK
      ctx.beginPath()
      ctx.moveTo(0, fr.sy(y))
      ctx.lineTo(fr.w, fr.sy(y))
      ctx.stroke()
    }
    ctx.restore()
  }

  if (props.marker) {
    ctx.save()
    ctx.beginPath()
    ctx.arc(fr.sx(props.marker[0]), fr.sy(props.marker[1]), 6, 0, 2 * Math.PI)
    ctx.fillStyle = 'white'
    ctx.fill()
    ctx.lineWidth = 2.2
    ctx.strokeStyle = INK
    ctx.stroke()
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
  <div class="cp">
    <span v-if="yLabel" class="ylab">{{ yLabel }}</span>
    <canvas ref="canvas" />
    <span v-if="xLabel" class="xlab">{{ xLabel }}</span>
  </div>
</template>

<style scoped>
.cp { position: relative; height: 100%; min-height: 0; display: flex; flex-direction: column; }
canvas { width: 100%; flex: 1 1 0; min-height: 0; display: block; }
.xlab { text-align: center; font-size: 0.78rem; margin-top: 0.1rem; }
.ylab {
  position: absolute; left: -1.5rem; top: 50%; transform: rotate(-90deg) translateX(-50%);
  font-size: 0.78rem;
}
</style>
