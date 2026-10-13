<!-- svm_kernel: a circle in 2D is a flat plane one dimension up.
     The first slider tilts the view from flat 2D to the lifted 3D picture;
     the second slides the cutting plane, and the circle it leaves behind. -->
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { rings } from '../lib/data'
import { frame } from '../lib/plot'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const data = rings(150, 1)
const z = data.X.map(([a, b]) => a * a + b * b)

const tilt = ref(0)     // 0 = seen from straight above, 1 = the lifted view
const height = ref(2.2) // where the plane cuts

const canvas = ref<HTMLCanvasElement | null>(null)
let queued = 0

/** Interpolate between a top-down view and matplotlib's view_init(16, -62). */
function project(x: number, y: number, zz: number, t: number): [number, number] {
  const elev = ((90 - 74 * t) * Math.PI) / 180
  const azim = ((-62 * t) * Math.PI) / 180
  const ca = Math.cos(azim), sa = Math.sin(azim)
  const xr = x * ca - y * sa
  const yr = x * sa + y * ca
  const ce = Math.cos(elev), se = Math.sin(elev)
  // z only shows up as the view tilts away from vertical
  const sx = xr
  const sy = yr * se - (zz - 2.5) * ce * 0.55
  return [sx, sy]
}

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth) return
  const t = tilt.value
  const fr = frame(el, [-3.6, 3.6, -3.4, 3.4])
  const { ctx } = fr
  const P = (x: number, y: number, zz: number) => {
    const [sx, sy] = project(x, y, zz, t)
    return [fr.sx(sx), fr.sy(sy)] as [number, number]
  }

  // the cutting plane, drawn as a grid so the tilt reads
  ctx.save()
  ctx.strokeStyle = MUTED
  ctx.globalAlpha = 0.5
  ctx.lineWidth = 0.8
  const lim = 2.6
  for (let i = 0; i <= 8; i++) {
    const v = -lim + (2 * lim * i) / 8
    ctx.beginPath()
    let p = P(v, -lim, height.value)
    ctx.moveTo(p[0], p[1])
    p = P(v, lim, height.value)
    ctx.lineTo(p[0], p[1])
    ctx.stroke()
    ctx.beginPath()
    p = P(-lim, v, height.value)
    ctx.moveTo(p[0], p[1])
    p = P(lim, v, height.value)
    ctx.lineTo(p[0], p[1])
    ctx.stroke()
  }
  ctx.restore()

  // the circle the plane leaves behind, down on the x1-x2 floor
  const r = Math.sqrt(Math.max(0, height.value))
  ctx.save()
  ctx.strokeStyle = GREEN
  ctx.lineWidth = 2.2
  ctx.beginPath()
  for (let i = 0; i <= 120; i++) {
    const a = (2 * Math.PI * i) / 120
    const [px, py] = P(r * Math.cos(a), r * Math.sin(a), 0)
    if (i === 0) ctx.moveTo(px, py)
    else ctx.lineTo(px, py)
  }
  ctx.stroke()
  ctx.restore()

  // points, painted back to front so the lifted view looks right
  const order = data.X.map((_, i) => i).sort((a, b) => {
    const pa = project(data.X[a][0], data.X[a][1], z[a], t)
    const pb = project(data.X[b][0], data.X[b][1], z[b], t)
    return pb[1] - pa[1]
  })
  for (const i of order) {
    const [px, py] = P(data.X[i][0], data.X[i][1], z[i] * t)
    ctx.fillStyle = data.y[i] === 1 ? RED : BLUE
    ctx.beginPath()
    if (data.y[i] === 1) {
      ctx.moveTo(px, py - 4.4)
      ctx.lineTo(px + 3.9, py + 3.1)
      ctx.lineTo(px - 3.9, py + 3.1)
      ctx.closePath()
    } else ctx.arc(px, py, 3.4, 0, 2 * Math.PI)
    ctx.fill()
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
watch([tilt, height], schedule)

const radius = computed(() => Math.sqrt(Math.max(0, height.value)))
const split = computed(() => {
  let wrong = 0
  for (let i = 0; i < z.length; i++) {
    const above = z[i] > height.value
    if (above !== (data.y[i] === 1)) wrong++
  }
  return wrong
})
</script>

<template>
  <div class="wrap">
    <canvas ref="canvas" />
    <div class="side">
      <Knob v-model="tilt" :min="0" :max="1" :step="0.01" label="lift into 3D" :digits="2" :color="INK" />
      <Knob v-model="height" :min="0.2" :max="5" :step="0.02" label="cut at height" :digits="2" :color="GREEN" />
      <p class="eq">add a column &nbsp;z = x₁² + x₂²</p>
      <Readout
        :items="[
          { label: 'plane', value: `z = ${height.toFixed(2)}`, color: MUTED },
          { label: 'circle radius', value: radius.toFixed(2), color: GREEN },
          { label: 'points on the wrong side', value: String(split), color: split ? '#c53030' : GREEN },
        ]"
      />
      <p class="note">
        no straight line works in the plane. One dimension up, a flat plane
        separates the two rings — and back in 2D that plane is a circle.
      </p>
      <p class="note strong">
        the kernel computes the lifted inner products without ever building the
        extra column
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
canvas { width: 100%; height: 100%; min-height: 0; display: block; }
.side { display: flex; flex-direction: column; gap: 0.5rem; }
.eq { font-size: 0.95rem; margin: 0.2rem 0 0; }
.note { font-size: 0.78rem; color: v-bind(MUTED); margin: 0; line-height: 1.45; }
.note.strong { color: v-bind(INK); }
</style>
