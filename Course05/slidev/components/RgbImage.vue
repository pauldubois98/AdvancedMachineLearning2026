<!-- A small colour image (the hyperspectral scene), scaled up crisply, with an
     optional square around one pixel. -->
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{ width: number; height: number; rgb: (q: number) => [number, number, number]; mark?: [number, number] | null; version?: number }>(),
  { mark: null, version: 0 },
)
const canvas = ref<HTMLCanvasElement | null>(null)
let ro: ResizeObserver | null = null
function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth) return
  const s = Math.min(el.clientWidth / props.width, el.clientHeight / props.height)
  const w = s * props.width
  const h = s * props.height
  const ox = (el.clientWidth - w) / 2
  const oy = (el.clientHeight - h) / 2
  const dpr = window.devicePixelRatio || 1
  el.width = Math.round(el.clientWidth * dpr)
  el.height = Math.round(el.clientHeight * dpr)
  const ctx = el.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  const off = document.createElement('canvas')
  off.width = props.width
  off.height = props.height
  const octx = off.getContext('2d')!
  const img = octx.createImageData(props.width, props.height)
  for (let q = 0; q < props.width * props.height; q++) {
    const [r, g, b] = props.rgb(q)
    img.data[4 * q] = 255 * r
    img.data[4 * q + 1] = 255 * g
    img.data[4 * q + 2] = 255 * b
    img.data[4 * q + 3] = 255
  }
  octx.putImageData(img, 0, 0)
  ctx.imageSmoothingEnabled = false
  ctx.drawImage(off, ox, oy, w, h)
  if (props.mark) {
    ctx.strokeStyle = '#1b1b1b'
    ctx.lineWidth = 2
    ctx.strokeRect(ox + (props.mark[0] - 1) * s, oy + (props.mark[1] - 1) * s, 3 * s, 3 * s)
  }
}
onMounted(() => { draw(); ro = new ResizeObserver(draw); if (canvas.value) ro.observe(canvas.value) })
onBeforeUnmount(() => ro?.disconnect())
watch(() => [props.mark, props.version, props.rgb], draw)
</script>

<template>
  <canvas ref="canvas" class="rgbimg" />
</template>

<style scoped>
.rgbimg { width: 100%; height: 100%; display: block; min-height: 0; }
</style>
