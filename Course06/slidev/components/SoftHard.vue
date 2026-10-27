<!-- soft_vs_hard: the same fit, read two ways. Soft keeps the doubt; hard
     throws it away. The threshold marks the points with no clear owner. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { argmax, em2, kmeansStart, resp2, sampleMix2, type Mix2 } from '../lib/gmm'
import { COMP, GOLD, RED, INK } from '../lib/theme'

const truth: Mix2 = { p: [0.55, 0.45], mu: [[-0.75, -0.25], [0.8, 0.4]], S: [[0.95, 0.52, 0.4], [0.7, -0.4, 0.48]] }
const { X } = sampleMix2(truth, 260, 12)
const h = em2(X, kmeansStart(X, 2, 0), 80)
const fit = h[h.length - 1]
const g = X.map((x) => resp2(x, fit))
const mode = ref('soft')
const thr = ref(0.9)
// blue at gamma_1 = 1, through pale, to gold at gamma_1 = 0
function mixColor(v: number): string {
  const a = [183, 121, 31], m1 = [239, 230, 210], m2 = [232, 238, 245], b = [43, 108, 176]
  const lerp = (u: number[], w: number[], t: number) => u.map((c, i) => Math.round(c + t * (w[i] - c)))
  const c = v < 1 / 3 ? lerp(a, m1, v * 3) : v < 2 / 3 ? lerp(m1, m2, (v - 1 / 3) * 3) : lerp(m2, b, (v - 2 / 3) * 3)
  return `rgb(${c[0]},${c[1]},${c[2]})`
}
const colors = computed(() => g.map((r) => (mode.value === 'soft' ? mixColor(r[0]) : COMP[argmax(r)])))
const unsure = computed(() => g.map((r, i) => (Math.max(...r) < thr.value ? i : -1)).filter((i) => i >= 0))
</script>

<template>
  <div class="wrap">
    <div class="note top">Soft assignment keeps the doubt; hard assignment throws it away</div>
    <div class="body">
      <Plane
        :X="X" :colors="colors" :size="4" :alpha="0.95" :domain="[-3.4, 3.4, -2.4, 2.4]"
        :ellipses="fit.mu.map((mu, k) => ({ mu, S: fit.S[k], color: COMP[k], width: 1.4 }))"
        :markers="unsure.map((i) => ({ at: X[i], color: INK, shape: 'ring', size: 6 }))"
        :title="mode === 'soft' ? 'soft: a weight per component' : 'hard: one label'" :title-color="mode === 'soft' ? GOLD : RED"
      />
      <div class="side">
        <div class="h" :style="{ color: GOLD }">Soft benefits</div>
        <p>— points between the clusters are uncertain</p>
        <p>— the estimation step weights them instead of mis-assigning them</p>
        <p>— stays differentiable in θ</p>
        <p class="big"><b>{{ unsure.length }}</b> of these {{ X.length }} points have no component above {{ thr.toFixed(2) }} (ringed)</p>
        <div class="key"><span :style="{ color: COMP[1] }">γᵢ₁ = 0</span><span class="bar" /><span :style="{ color: COMP[0] }">1</span></div>
      </div>
    </div>
    <div class="controls">
      <Choice v-model="mode" :options="[{ value: 'soft', label: 'soft', color: GOLD }, { value: 'hard', label: 'hard', color: RED }]" label="assignment" />
      <Knob v-model="thr" :min="0.5" :max="0.999" :step="0.001" label="certainty threshold" :digits="3" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1.4fr 1fr; gap: 2rem; min-height: 0; }
.side { align-self: center; }
.big { margin: 0.7rem 0; }
.key { display: flex; align-items: center; gap: 0.4rem; font-size: 0.78rem; }
.bar { width: 8rem; height: 0.6rem; border-radius: 2px; background: linear-gradient(90deg, #b7791f, #efe6d2, #e8eef5, #2b6cb0); }
</style>
