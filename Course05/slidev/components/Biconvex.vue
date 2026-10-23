<!-- biconvex_picture: f(w, h) = ½(x - wh)² with x = 1. The valley wh = 1 is
     not a bowl, but freeze one variable and what is left is a plain parabola.
     Move the frozen value: the slice moves on the map, its parabola on the
     right. -->
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { range } from '../lib/losses'
import { BLUE, GREEN, INK, PURPLE, RED, RAMPS } from '../lib/theme'

const frozen = ref<'h' | 'w'>('h')
const v = ref(1.2)
const f = (w: number, h: number) => 0.5 * (1 - w * h) ** 2
const LIM = 3
const canvas = ref<HTMLCanvasElement | null>(null)
let ro: ResizeObserver | null = null
function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth) return
  const S = Math.min(el.clientWidth, el.clientHeight)
  const ox = (el.clientWidth - S) / 2
  const dpr = window.devicePixelRatio || 1
  el.width = Math.round(el.clientWidth * dpr)
  el.height = Math.round(el.clientHeight * dpr)
  const ctx = el.getContext('2d')!
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
  const N = 160
  const off = document.createElement('canvas')
  off.width = N
  off.height = N
  const octx = off.getContext('2d')!
  const img = octx.createImageData(N, N)
  for (let i = 0; i < N; i++) for (let j = 0; j < N; j++) {
    const w = ((j + 0.5) / N) * LIM
    const h = (1 - (i + 0.5) / N) * LIM
    // bands of the loss, dark in the valley
    const t = Math.floor(Math.exp(-2.2 * f(w, h)) * 14) / 14
    const [r, g, b] = RAMPS.x(t)
    const k = 4 * (i * N + j)
    img.data[k] = r; img.data[k + 1] = g; img.data[k + 2] = b; img.data[k + 3] = 255
  }
  octx.putImageData(img, 0, 0)
  ctx.drawImage(off, ox, 0, S, S)
  const sx = (w: number) => ox + (w / LIM) * S
  const sy = (h: number) => (1 - h / LIM) * S
  ctx.strokeStyle = RED
  ctx.lineWidth = 2.2
  ctx.beginPath()
  range(1 / LIM, LIM, 120).forEach((w, i) => { const h = 1 / w; i ? ctx.lineTo(sx(w), sy(h)) : ctx.moveTo(sx(w), sy(h)) })
  ctx.stroke()
  ctx.strokeStyle = PURPLE
  ctx.lineWidth = 2.4
  ctx.setLineDash([6, 4])
  ctx.beginPath()
  if (frozen.value === 'h') { ctx.moveTo(sx(0), sy(v.value)); ctx.lineTo(sx(LIM), sy(v.value)) }
  else { ctx.moveTo(sx(v.value), sy(0)); ctx.lineTo(sx(v.value), sy(LIM)) }
  ctx.stroke()
  ctx.setLineDash([])
  const [mw, mh] = frozen.value === 'h' ? [1 / v.value, v.value] : [v.value, 1 / v.value]
  if (mw <= LIM && mh <= LIM) {
    ctx.fillStyle = GREEN
    ctx.beginPath(); ctx.arc(sx(mw), sy(mh), 6, 0, 2 * Math.PI); ctx.fill()
  }
  ctx.fillStyle = INK
  ctx.font = '13px Lato, sans-serif'
  ctx.fillText('w →', ox + S - 34, S - 6)
  ctx.fillText('h ↑', ox + 6, 16)
  ctx.fillStyle = RED
  ctx.fillText('every point of this curve', sx(1.55), sy(2.55))
  ctx.fillText('is a global minimum', sx(1.55), sy(2.55) + 16)
}
onMounted(() => { draw(); ro = new ResizeObserver(draw); if (canvas.value) ro.observe(canvas.value) })
onBeforeUnmount(() => ro?.disconnect())
watch([v, frozen], draw)
const ws = range(0, LIM, 200)
const slice = computed(() => ws.map((u) => [u, frozen.value === 'h' ? f(u, v.value) : f(v.value, u)] as [number, number]))
</script>

<template>
  <div class="wrap">
    <div class="panels">
      <div class="col">
        <div class="title">f(w, h) = ½(x − wh)² with x = 1</div>
        <canvas ref="canvas" />
        <div class="cap">a non-convex valley, not a bowl</div>
      </div>
      <div class="col">
        <LineChart
          :series="[{ points: slice, color: PURPLE, width: 2.6 }]"
          :dots="[{ x: 1 / v, y: 0, color: GREEN, r: 5 }]"
          :x-domain="[0, LIM]" :y-domain="[0, 1.25]" :x-label="frozen === 'h' ? 'w' : 'h'" :x-ticks="[0, 0.5, 1, 1.5, 2, 2.5, 3]" :y-ticks="[0, 0.25, 0.5, 0.75, 1]"
          :title="`one slice: ${frozen} = ${v.toFixed(2)} fixed`" :title-color="PURPLE"
        />
        <div class="cap">but each slice is a plain parabola, with its minimum on the valley floor</div>
      </div>
    </div>
    <div class="controls">
      <Choice v-model="frozen" label="freeze" :options="[{ value: 'h', label: 'h', color: PURPLE }, { value: 'w', label: 'w', color: PURPLE }]" />
      <Knob v-model="v" :min="0.35" :max="2.9" :step="0.01" :label="`frozen ${frozen}`" :color="PURPLE" />
      <span class="note">Alternating minimization jumps straight onto the red curve, whichever slice it starts from.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.panels { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; min-height: 0; }
.col { display: grid; grid-template-rows: auto 1fr auto; gap: 0.3rem; min-height: 0; }
.col:last-child { grid-template-rows: 1fr auto; }
.title { text-align: center; font-weight: 600; font-size: 0.85rem; }
canvas { width: 100%; height: 100%; min-height: 0; display: block; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.8rem; }
</style>
