<!-- svm_which: four lines with zero training error. Reveal the street each
     one would get, and the training error stops being able to choose. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { sepBlobs } from '../lib/data'
import { GOLD, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const data = sepBlobs(90, 2.6, 3)
const candidates = [
  { a: -1.506, c: -0.727, color: PURPLE },
  { a: -1.49, c: -0.11, color: GOLD },
  { a: -0.95, c: 0.1, color: RED },
  { a: -2.6, c: -0.55, color: GREEN },
]
const show = ref(false)
const pick = ref(-1)

function halfWidth(a: number, c: number): number {
  let best = Infinity
  for (const [x, y] of data.X)
    best = Math.min(best, Math.abs(a * x - y + c) / Math.hypot(a, 1))
  return best
}
const widths = computed(() => candidates.map((l) => 2 * halfWidth(l.a, l.c)))
const widest = computed(() => widths.value.indexOf(Math.max(...widths.value)))

const lines = computed(() =>
  candidates.map((l, i) => ({
    a: l.a, c: l.c,
    color: show.value ? l.color : MUTED,
    width: pick.value === i ? 2.8 : 2,
    dash: show.value && pick.value === i ? [] : [6, 5],
  })),
)
const band = computed(() => {
  if (!show.value || pick.value < 0) return null
  const l = candidates[pick.value]
  return { a: l.a, c: l.c, half: halfWidth(l.a, l.c), color: l.color, alpha: 0.3 }
})
</script>

<template>
  <div class="wrap">
    <FieldPlot :X="data.X" :y="data.y" :lines="lines" :band="band" :point-size="30" />
    <div class="controls">
      <p class="title">all four separate the training data perfectly</p>
      <div class="row">
        <Toggle v-model="show" label="show the street each line gets" :color="GREEN" />
        <span class="hint">hover a line below</span>
      </div>
      <div class="cards">
        <div
          v-for="(l, i) in candidates" :key="i" class="card"
          :class="{ on: pick === i, best: show && widest === i }"
          :style="{ borderColor: pick === i ? l.color : '#e3e5e8' }"
          @mouseenter="pick = i" @mouseleave="pick = -1"
        >
          <span class="dot" :style="{ background: l.color }" />
          <span class="name">line {{ i + 1 }}</span>
          <span class="val" :style="{ color: show ? l.color : MUTED }">
            {{ show ? widths[i].toFixed(2) : '—' }}
          </span>
        </div>
      </div>
      <p class="note" :style="{ color: show ? INK : RED }">
        <template v-if="show">
          the widest street belongs to line {{ widest + 1 }} — that is the one the SVM picks
        </template>
        <template v-else>
          the training error cannot choose between them — something else has to
        </template>
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.25fr 1fr; gap: 1.4rem; height: 100%; min-height: 0; align-items: center; }
.controls { display: flex; flex-direction: column; gap: 0.5rem; }
.title { font-size: 0.95rem; margin: 0; }
.row { display: flex; align-items: center; gap: 0.8rem; }
.hint { color: v-bind(MUTED); font-size: 0.72rem; }
.cards { display: flex; flex-direction: column; gap: 0.25rem; }
.card {
  display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 0.5rem;
  border: 1px solid #e3e5e8; border-radius: 0.35rem; padding: 0.22rem 0.55rem;
  font-size: 0.82rem; transition: all 0.12s;
}
.card.best { background: #f4fbf4; }
.dot { width: 0.55rem; height: 0.55rem; border-radius: 50%; display: inline-block; }
.val { font-variant-numeric: tabular-nums; font-weight: 600; }
.note { font-size: 0.8rem; margin: 0.2rem 0 0; }
</style>
