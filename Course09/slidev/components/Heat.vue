<!-- A probability matrix drawn as cells, white at zero, on a square-root
     scale so the small probabilities still show (the printed figures'
     PowerNorm(0.5)). Coloured bars along the edges mark the toy's groups. -->
<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { COMP, GRID, INK, heat } from '../lib/theme'

const props = withDefaults(defineProps<{
  M: Float64Array | number[]
  n: number
  groups?: number[]
  vmax?: number
  title?: string
  titleColor?: string
}>(), { groups: () => [], title: '', titleColor: INK })

const canvas = ref<HTMLCanvasElement | null>(null)
let ro: ResizeObserver | null = null

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth) return
  const dpr = window.devicePixelRatio || 1
  const W = el.clientWidth, H = el.clientHeight
  el.width = W * dpr; el.height = H * dpr
  const ctx = el.getContext('2d')!
  ctx.scale(dpr, dpr)
  ctx.clearRect(0, 0, W, H)
  const n = props.n
  const bar = props.groups.length ? 7 : 0
  const side = Math.min(W, H) - bar - 2
  const x0 = (W - side - bar) / 2 + bar, y0 = (H - side - bar) / 2 + bar
  const c = side / n
  let vmax = props.vmax ?? 0
  if (!vmax) for (let a = 0; a < n * n; a++) if (props.M[a] > vmax) vmax = props.M[a]
  for (let i = 0; i < n; i++)
    for (let j = 0; j < n; j++) {
      const v = Math.sqrt(Math.max(0, Math.min(1, props.M[i * n + j] / vmax)))
      const [r, g, b] = heat(v)
      ctx.fillStyle = `rgb(${r},${g},${b})`
      ctx.fillRect(x0 + j * c, y0 + i * c, c + 0.6, c + 0.6)
    }
  if (props.groups.length) {
    let start = 0
    for (let i = 1; i <= n; i++) {
      if (i === n || props.groups[i] !== props.groups[start]) {
        const col = COMP[props.groups[start] % COMP.length]
        ctx.fillStyle = col
        ctx.fillRect(x0 - bar - 1, y0 + start * c, bar, (i - start) * c)
        ctx.fillRect(x0 + start * c, y0 - bar - 1, (i - start) * c, bar)
        if (i < n) {
          ctx.strokeStyle = GRID; ctx.lineWidth = 0.8
          ctx.beginPath()
          ctx.moveTo(x0, y0 + i * c); ctx.lineTo(x0 + side, y0 + i * c)
          ctx.moveTo(x0 + i * c, y0); ctx.lineTo(x0 + i * c, y0 + side)
          ctx.stroke()
        }
        start = i
      }
    }
  }
}
let q = 0
const schedule = () => { if (!q) q = requestAnimationFrame(() => { q = 0; draw() }) }
onMounted(() => { draw(); ro = new ResizeObserver(schedule); if (canvas.value) ro.observe(canvas.value) })
onBeforeUnmount(() => ro?.disconnect())
watch(() => [props.M, props.vmax], schedule)
</script>

<template>
  <figure class="heat">
    <figcaption v-if="title" :style="{ color: titleColor }" v-html="title" />
    <canvas ref="canvas" />
  </figure>
</template>

<style scoped>
.heat { display: flex; flex-direction: column; margin: 0; min-height: 0; height: 100%; }
figcaption { text-align: center; font-size: 0.85rem; font-weight: 600; margin-bottom: 0.2rem; }
canvas { flex: 1 1 0; min-height: 0; width: 100%; display: block; }
</style>
