<!-- regression_setting: inputs and labels go in, a line f_beta comes out. The
     sliders change the data the line is learnt from. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { fitLine, fmt, lineData } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import { BLUE, GREEN, MUTED, PURPLE } from '../lib/theme'

const n = ref(50)
const noise = ref(0.9)
const slope = ref(1.1)
const seed = ref(3)
const data = computed(() => lineData(new Rng(seed.value), n.value, noise.value, slope.value))
const beta = computed(() => fitLine(data.value.x, data.value.y))
const X = computed(() => data.value.x.map((v, i) => [v, data.value.y[i]] as [number, number]))
</script>

<template>
  <div class="cmp">
    <div class="r23" style="align-items: center">
      <div class="setflow">
        <div class="box blue">X = (x₁, …, x<sub>n</sub>)<div class="sub">inputs</div></div>
        <div class="box green">y = (y₁, …, y<sub>n</sub>)<div class="sub">labels, y ∈ ℝ</div></div>
        <div class="arrow">→</div>
        <div class="box purple big">learn f<sub>β</sub></div>
        <div class="arrow">→</div>
      </div>
      <Plane :X="X" :colors="BLUE" :size="3.5" :alpha="0.65" :domain="[-3.3, 3.3, -6, 6]" :equal="false" axes x-label="x" y-label="y"
        :segments="[lineSeg(beta, -3.3, 3.3, PURPLE, 2.6)]" />
    </div>
    <div class="foot">the fitted line ŷ = <b :style="{ color: PURPLE }">{{ fmt(beta[0]) }} + {{ fmt(beta[1]) }} x</b>; the data was drawn from y = 0.6 + {{ fmt(slope) }} x + noise</div>
    <div class="controls">
      <Knob v-model="n" :min="5" :max="300" :step="1" :digits="0" label="n" :color="BLUE" />
      <Knob v-model="noise" :min="0" :max="3" :step="0.05" label="noise σ" :color="MUTED" />
      <Knob v-model="slope" :min="-2" :max="2" :step="0.05" label="true slope" :color="GREEN" />
      <Knob v-model="seed" :min="1" :max="40" :step="1" :digits="0" label="new sample" :color="BLUE" />
    </div>
  </div>
</template>

<style scoped>
.setflow { display: grid; grid-template-columns: 1fr auto 1fr auto; grid-template-rows: 1fr 1fr; gap: 0.8rem 0.6rem; align-items: center; }
.setflow .box.blue { grid-column: 1; grid-row: 1; }
.setflow .box.green { grid-column: 1; grid-row: 2; }
.setflow .arrow { grid-row: 1 / 3; color: var(--muted); font-size: 1.6rem; }
.setflow .big { grid-row: 1 / 3; font-size: 1.2rem; padding: 1rem 0.6rem; }
.sub { font-size: 0.75rem; color: var(--muted); margin-top: 0.2rem; }
</style>
