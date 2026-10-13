<!-- duality_saddle: L(w, α) = ½w² − α(w − 1) for min ½w² s.t. w ≥ 1.
     Move w and α by hand: the solution is a saddle, lowest along w and
     highest along α, so the two orders of min and max agree. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, INK, MUTED } from '../lib/theme'

const w = ref(1.7)
const alpha = ref(0.6)

const L = (ww: number, aa: number) => 0.5 * ww * ww - aa * (ww - 1)
const value = computed(() => L(w.value, alpha.value))

/** for the current α, the w that minimises L is w = α (unconstrained in w) */
const argminW = computed(() => alpha.value)
/** for the current w, L grows or shrinks without bound in α unless w = 1 */
const alphaDirection = computed(() => (w.value > 1 ? 'down' : w.value < 1 ? 'up' : 'flat'))

const dual = computed(() => alpha.value - (alpha.value * alpha.value) / 2) // min_w L
const curveDual: [number, number][] = []
for (let i = 0; i <= 120; i++) {
  const a = (2.4 * i) / 120
  curveDual.push([a, a - (a * a) / 2])
}
const curvePrimal: [number, number][] = []
for (let i = 0; i <= 120; i++) {
  const ww = -0.4 + (3.0 * i) / 120
  curvePrimal.push([ww, ww >= 1 ? 0.5 * ww * ww : Infinity])
}
</script>

<template>
  <div class="wrap">
    <div class="left">
      <ContourPlot
        :f="L" :domain="[-0.4, 2.6, 0, 2.4]" :vmin="-1.2" :vmax="2.6" :levels="[0.5]"
        :marker="[w, alpha]" :crosshair="{ x: w, y: alpha, xColor: BLUE, yColor: GREEN }"
        x-label="w" y-label="α"
      />
    </div>
    <div class="side">
      <p class="eq">L(w, α) = ½w² − α(w − 1)</p>
      <p class="sub">the Lagrangian of &nbsp;min ½w² &nbsp;s.t.&nbsp; w ≥ 1</p>
      <Knob v-model="w" :min="-0.4" :max="2.6" :step="0.01" label="w" :color="BLUE" />
      <Knob v-model="alpha" :min="0" :max="2.4" :step="0.01" label="α" :color="GREEN" />
      <p class="val">L = <strong>{{ value.toFixed(3) }}</strong></p>
      <ul>
        <li :style="{ color: BLUE }">
          along w: L is a parabola, lowest at w = α = {{ argminW.toFixed(2) }}
        </li>
        <li :style="{ color: GREEN }">
          along α: L is a straight line —
          <template v-if="alphaDirection === 'down'">w &gt; 1, so raising α lowers L: the constraint is loose, α wants to be 0</template>
          <template v-else-if="alphaDirection === 'up'">w &lt; 1, so raising α raises L without bound: the constraint is violated</template>
          <template v-else>w = 1 exactly, so α does not change L at all</template>
        </li>
      </ul>
      <p class="saddle" :class="{ on: Math.abs(w - 1) < 0.04 && Math.abs(alpha - 1) < 0.04 }">
        a saddle, not a peak — at (ŵ, α̂) = (1, 1):
        min<sub>w</sub> max<sub>α</sub> L = max<sub>α</sub> min<sub>w</sub> L = 0.5
        <button @click="w = 1; alpha = 1">go there</button>
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; height: 100%; min-height: 0; align-items: center; }
.left { height: 100%; min-height: 0; padding-left: 1.3rem; }
.side { display: flex; flex-direction: column; gap: 0.4rem; }
.eq { font-size: 1.05rem; margin: 0; }
.sub { color: v-bind(MUTED); font-size: 0.78rem; margin: 0 0 0.3rem; }
.val { font-size: 0.95rem; margin: 0.2rem 0; font-variant-numeric: tabular-nums; }
ul { margin: 0; padding-left: 1rem; font-size: 0.78rem; line-height: 1.5; }
.saddle {
  font-size: 0.8rem; margin: 0.3rem 0 0; padding: 0.4rem 0.6rem;
  border: 1px solid #e3e5e8; border-radius: 0.35rem; color: v-bind(MUTED);
}
.saddle.on { color: v-bind(GREEN); border-color: v-bind(GREEN); background: #f4fbf4; }
button {
  border: 1px solid #d8dadd; background: white; border-radius: 0.3rem;
  padding: 0.08rem 0.4rem; font-size: 0.72rem; cursor: pointer; margin-left: 0.3rem;
}
</style>
