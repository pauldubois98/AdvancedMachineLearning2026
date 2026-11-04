<!-- outliers_vs_mismodelling: a robust loss fixes a few wrong points, never a
     wrong model. Left, two outliers; right, a curved truth fitted by a line. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { fitLine, irls, outlierBase, wHuber } from '../lib/reg'
import { lineSeg } from '../lib/draw'
import { BLUE, GOLD, GREEN, RED } from '../lib/theme'

const far = ref(1)
const curv = ref(0.45)
const base = outlierBase(13)
const ox = [2.35, -2.2]
const oy = computed(() => [-5.4 * far.value, 5.0 * far.value])
const xs = computed(() => [...base.x, ...ox])
const ys = computed(() => [...base.y, ...oy.value])
const lsL = computed(() => fitLine(xs.value, ys.value))
const huL = computed(() => irls(xs.value, ys.value, (e) => wHuber(e, 1.345)).at(-1)!.beta)
const rng = new Rng(14)
const z = Array.from({ length: 40 }, () => rng.normal(0, 0.35))
const xc = Array.from({ length: 40 }, (_, i) => -3 + (6 * i) / 39)
const yc = computed(() => xc.map((v, i) => curv.value * v * v - 0.8 + z[i]))
const lsR = computed(() => fitLine(xc, yc.value))
const huR = computed(() => irls(xc, yc.value, (e) => wHuber(e, 1.345)).at(-1)!.beta)
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="xs.map((v, i) => [v, ys[i]])" :colors="xs.map((_, i) => (i >= 26 ? RED : BLUE))" :sizes="xs.map((_, i) => (i >= 26 ? 6 : 3.5))" :alpha="0.8"
        :domain="[-3.5, 3.5, -8, 8]" :equal="false" :segments="[lineSeg(lsL, -3.5, 3.5, GOLD, 2.2), lineSeg(huL, -3.5, 3.5, GREEN, 2.4)]"
        title="outliers" :title-color="RED" caption="the model is right, a few points are off: Huber (green) ignores them" />
      <Plane :X="xc.map((v, i) => [v, yc[i]])" :colors="BLUE" :size="3.5" :alpha="0.8" :domain="[-3.5, 3.5, -2.5, 4.5]" :equal="false"
        :segments="[lineSeg(lsR, -3.5, 3.5, GOLD, 2.2), lineSeg(huR, -3.5, 3.5, GREEN, 2.4)]"
        title="mismodelling" :title-color="GOLD" caption="the model is wrong: no loss can fix a straight line" />
    </div>
    <div class="foot"><span :style="{ color: GOLD }">least squares</span> and <span :style="{ color: GREEN }">Huber</span> on both: robustness against outliers is not a cure for a model that is too simple</div>
    <div class="controls">
      <Knob v-model="far" :min="0" :max="1.6" :step="0.01" label="how far the outliers are" :color="RED" />
      <Knob v-model="curv" :min="0" :max="0.6" :step="0.01" label="curvature of the truth" :color="GOLD" />
    </div>
  </div>
</template>
