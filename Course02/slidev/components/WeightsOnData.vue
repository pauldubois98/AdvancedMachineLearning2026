<!-- weights_on_data: the robust fit gives every point a weight, small and pale
     for the far ones, without any hand-made outlier detection. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { fitLine, fmt, irls, outlierBase, wHuber, wTukey } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const base = outlierBase(7)
const y1 = ref(-5.4)
const y2 = ref(5.0)
const kind = ref('huber')
const X = [...base.x, 2.35, -2.2]
const Y = computed(() => [...base.y, y1.value, y2.value])
const ls = computed(() => fitLine(X, Y.value))
const rob = computed(() => irls(X, Y.value, kind.value === 'huber' ? (e) => wHuber(e, 1.345) : (e) => wTukey(e, 4.685), 30).at(-1)!)
const w = computed(() => rob.value.w)
const name = computed(() => (kind.value === 'huber' ? 'Huber' : 'Tukey'))
</script>

<template>
  <div class="cmp">
    <div class="r2" style="grid-template-columns: 2.4fr 1fr">
      <Plane :X="X.map((v, i) => [v, Y[i]])" :colors="BLUE" :sizes="w.map((v) => 3.5 + 5 * v)" :alphas="w.map((v) => 0.3 + 0.65 * v)"
        :domain="[-3.5, 3.5, -8, 8]" :equal="false" :segments="[lineSeg(ls, -3.5, 3.5, RED, 2.6), lineSeg(rob.beta, -3.5, 3.5, GREEN, 2.6)]"
        :texts="[{ at: [2.55, y1], text: `ω = ${fmt(w[26])}`, color: RED, size: 14 }, { at: [-2.0, y2], text: `ω = ${fmt(w[27])}`, color: RED, size: 14 }]" />
      <div class="side" style="align-self: center">
        <p><span :style="{ color: RED }">━ least squares</span>, β̂₁ = {{ fmt(ls[1]) }}</p>
        <p><span :style="{ color: GREEN }">━ {{ name }}</span>, β̂₁ = {{ fmt(rob.beta[1]) }}</p>
        <p class="h" :style="{ color: GREEN }">least squares: all points get the same weight</p>
        <p class="h" :style="{ color: RED }">robust: far points get small weights</p>
        <p class="note">no handcrafted outlier detection: the weights come out of the fit. Smallest weight among the 26 ordinary points: {{ fmt(Math.min(...w.slice(0, 26))) }}</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="y1" :min="-9" :max="6" :step="0.05" label="outlier 1, y" :color="RED" />
      <Knob v-model="y2" :min="-6" :max="9" :step="0.05" label="outlier 2, y" :color="RED" />
      <Choice v-model="kind" :options="[{ value: 'huber', label: 'Huber', color: BLUE }, { value: 'tukey', label: 'Tukey', color: RED }]" />
    </div>
  </div>
</template>

<style scoped>
.cmp { grid-template-rows: 1fr auto; }
</style>
