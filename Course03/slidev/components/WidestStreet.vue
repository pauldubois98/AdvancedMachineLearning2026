<!-- svm_margin: turn and shift the line yourself. The street is the widest
     empty band around it; the SVM is the line that makes it widest. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sepBlobs, toPm1 } from '../lib/data'
import { fitSvc, kernel } from '../lib/svm'
import { GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const data = sepBlobs(90, 2.6, 3)
const yPm = toPm1(data.y)
const best = fitSvc(data.X, yPm, 1000, kernel({ type: 'linear' }))

const angle = ref(-56.4) // degrees; the printed figure's line
const offset = ref(-0.73)
const showBest = ref(false)

const slope = computed(() => Math.tan((angle.value * Math.PI) / 180))

/** distance of every point to the line, and which side it falls on */
const fit = computed(() => {
  const a = slope.value
  const c = offset.value
  const n = Math.hypot(a, 1)
  let half = Infinity
  let wrong = 0
  const wrongIdx: number[] = []
  for (let i = 0; i < data.X.length; i++) {
    const [x, y] = data.X[i]
    const signed = (y - a * x - c) / n // > 0 above the line
    half = Math.min(half, Math.abs(signed))
    // class 1 sits above the line in this dataset
    const ok = data.y[i] === 1 ? signed > 0 : signed < 0
    if (!ok) {
      wrong++
      wrongIdx.push(i)
    }
  }
  return { half, wrong, wrongIdx, width: 2 * half }
})

const bestWidth = computed(() => best.marginWidth ?? 0)
const ratio = computed(() => (fit.value.wrong ? 0 : fit.value.width / bestWidth.value))

// f(x) = w1 x1 + w2 x2 - b = 0  =>  x2 = (-w1 x1 + b) / w2
const bestLine = computed(() => {
  if (!best.w) return null
  const [w1, w2] = best.w
  return { a: -w1 / w2, c: best.b / w2 }
})
const allLines = computed(() => {
  const out: any[] = [
    { a: slope.value, c: offset.value, color: fit.value.wrong ? RED : GOLD, width: 2.2 },
  ]
  if (showBest.value && bestLine.value)
    out.push({ a: bestLine.value.a, c: bestLine.value.c, color: GREEN, width: 2.2 })
  return out
})
const band = computed(() =>
  fit.value.wrong
    ? null
    : { a: slope.value, c: offset.value, half: fit.value.half, color: GOLD, alpha: 0.3 },
)
const rings = computed(() => {
  const out: any[] = []
  if (fit.value.wrong) out.push({ idx: fit.value.wrongIdx, color: RED, size: 110, width: 1.6 })
  if (showBest.value) out.push({ idx: best.sv, color: GREEN, size: 140, width: 2 })
  return out
})

function snap() {
  if (!bestLine.value) return
  angle.value = (Math.atan(bestLine.value.a) * 180) / Math.PI
  offset.value = bestLine.value.c
  showBest.value = true
}
</script>

<template>
  <div class="wrap">
    <FieldPlot
      :X="data.X" :y="data.y" :lines="allLines" :band="band" :rings="rings" :point-size="28"
    />
    <div class="side">
      <div class="knobs">
        <Knob v-model="angle" :min="-89" :max="-10" :step="0.2" label="turn the line" unit="°" :digits="1" :color="GOLD" />
        <Knob v-model="offset" :min="-2.6" :max="2.6" :step="0.02" label="shift the line" :color="GOLD" />
      </div>
      <div class="box" :class="{ bad: fit.wrong > 0 }">
        <template v-if="fit.wrong">
          <p class="big" :style="{ color: RED }">{{ fit.wrong }} point{{ fit.wrong > 1 ? 's' : '' }} on the wrong side</p>
          <p class="sub">no street at all; the line has to separate first</p>
        </template>
        <template v-else>
          <p class="big" :style="{ color: GOLD }">street {{ fit.width.toFixed(2) }} wide</p>
          <div class="bar">
            <div class="fill" :style="{ width: `${Math.min(100, ratio * 100)}%`, background: ratio > 0.995 ? GREEN : GOLD }" />
          </div>
          <p class="sub">{{ (ratio * 100).toFixed(0) }}% of the widest street there is</p>
        </template>
      </div>
      <div class="row">
        <Toggle v-model="showBest" label="show the SVM line" :color="GREEN" />
        <button class="snap" @click="snap">snap to it</button>
      </div>
      <p v-if="showBest" class="sub green">
        the SVM line: street {{ bestWidth.toFixed(2) }} wide, equally close to both clouds;
        the circled points are the support vectors
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.2fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.side { display: flex; flex-direction: column; gap: 0.7rem; }
.knobs { display: flex; flex-direction: column; gap: 0.45rem; }
.box { border: 1px solid #e3e5e8; border-radius: 0.4rem; padding: 0.5rem 0.7rem; background: #fdfaf4; }
.box.bad { background: #fdf4f4; }
.big { font-size: 1.05rem; font-weight: 600; margin: 0; }
.sub { color: v-bind(MUTED); font-size: 0.76rem; margin: 0.15rem 0 0; }
.sub.green { color: v-bind(GREEN); }
.bar { height: 5px; background: #e8e9eb; border-radius: 3px; margin: 0.4rem 0 0; overflow: hidden; }
.fill { height: 100%; transition: width 0.1s linear; }
.row { display: flex; align-items: center; gap: 0.8rem; }
.snap {
  border: 1px solid #d8dadd; background: white; border-radius: 0.3rem;
  padding: 0.14rem 0.5rem; font-size: 0.76rem; cursor: pointer; color: v-bind(INK);
}
.snap:hover { border-color: v-bind(GREEN); color: v-bind(GREEN); }
</style>
