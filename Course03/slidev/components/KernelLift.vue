<!-- svm_kernel: a circle in 2D is a flat plane one dimension up.
     The first slider tilts the view from flat 2D, through the lifted 3D
     picture, to almost side-on; the second slides the cutting plane, and the
     circle it cuts out of the lifted points. -->
<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { rings } from '../lib/data'
import { frame } from '../lib/plot'
import { BLUE, GREEN, INK, MUTED, RED } from '../lib/theme'

const data = rings(150, 1)
const z = data.X.map(([a, b]) => a * a + b * b)

const tilt = ref(0)     // 0 = seen from straight above, 1 = almost side-on
const height = ref(2.2) // where the plane cuts

const canvas = ref<HTMLCanvasElement | null>(null)
let queued = 0

/** Interpolate between a top-down view and an almost side-on one, passing
 *  through matplotlib's view_init(16, -62) on the way. */
function view(t: number) {
  const elev = ((90 - 86 * t) * Math.PI) / 180
  const azim = ((-62 * t) * Math.PI) / 180
  return { ca: Math.cos(azim), sa: Math.sin(azim), ce: Math.cos(elev), se: Math.sin(elev) }
}
type View = ReturnType<typeof view>
function project(x: number, y: number, zz: number, v: View): [number, number] {
  const xr = x * v.ca - y * v.sa
  const yr = x * v.sa + y * v.ca
  // z only shows up as the view tilts away from vertical; up is up
  return [xr, yr * v.se + (zz - 2.5) * v.ce * 0.55]
}
/** how close a point is to the eye, to paint back to front */
function nearness(x: number, y: number, zz: number, v: View): number {
  const yr = x * v.sa + y * v.ca
  return -yr * v.ce + zz * v.se
}

function draw() {
  const el = canvas.value
  if (!el || !el.clientWidth) return
  const v = view(tilt.value)
  const h = height.value
  const fr = frame(el, [-3.6, 3.6, -3.4, 3.4])
  const { ctx } = fr
  const P = (x: number, y: number, zz: number) => {
    const [sx, sy] = project(x, y, zz, v)
    return [fr.sx(sx), fr.sy(sy)] as [number, number]
  }

  function points(below: boolean) {
    const idx = data.X.map((_, i) => i).filter((i) => (z[i] <= h) === below)
    idx.sort((a, b) => nearness(data.X[a][0], data.X[a][1], z[a], v) - nearness(data.X[b][0], data.X[b][1], z[b], v))
    for (const i of idx) {
      const [px, py] = P(data.X[i][0], data.X[i][1], z[i])
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

  // seen from above, the plane hides what is under it: paint the points
  // below it first, then the plane, then the points above
  points(true)

  // the cutting plane, filled lightly and drawn as a grid so the tilt reads
  const lim = 2.9
  ctx.save()
  ctx.fillStyle = MUTED
  ctx.globalAlpha = 0.22
  ctx.beginPath()
  for (const [a, b] of [[-lim, -lim], [lim, -lim], [lim, lim], [-lim, lim]]) {
    const p = P(a, b, h)
    ctx.lineTo(p[0], p[1])
  }
  ctx.closePath()
  ctx.fill()
  ctx.strokeStyle = MUTED
  ctx.globalAlpha = 0.6
  ctx.lineWidth = 0.8
  for (let i = 0; i <= 8; i++) {
    const u = -lim + (2 * lim * i) / 8
    for (const [a0, b0, a1, b1] of [[u, -lim, u, lim], [-lim, u, lim, u]]) {
      ctx.beginPath()
      let p = P(a0, b0, h)
      ctx.moveTo(p[0], p[1])
      p = P(a1, b1, h)
      ctx.lineTo(p[0], p[1])
      ctx.stroke()
    }
  }
  ctx.restore()

  // the circle where the plane cuts the paraboloid z = x1² + x2²: on the
  // plane itself, and straight above the 2D decision boundary
  const r = Math.sqrt(Math.max(0, h))
  ctx.save()
  ctx.strokeStyle = GREEN
  ctx.lineWidth = 2.4
  ctx.beginPath()
  for (let i = 0; i <= 120; i++) {
    const a = (2 * Math.PI * i) / 120
    const [px, py] = P(r * Math.cos(a), r * Math.sin(a), h)
    if (i === 0) ctx.moveTo(px, py)
    else ctx.lineTo(px, py)
  }
  ctx.stroke()
  ctx.restore()

  points(false)
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
        No straight line works in the plane. One dimension up, a flat plane
        separates the two rings, and back in 2D that plane is a circle.
      </p>
      <p class="note strong">
        The kernel computes the lifted inner products without ever building the
        extra column.
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
