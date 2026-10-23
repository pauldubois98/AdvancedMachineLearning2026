<!-- app_recsys: a table of ratings with holes, filled by weighted NMF: the
     missing cells get weight 0. Hide more of it, or change r. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ratings, ratingsMask } from '../lib/data5'
import { mul } from '../lib/mat'
import { fit, init } from '../lib/nmf'
import { GOLD, GREEN, INK } from '../lib/theme'

const hide = ref(0.55)
const r = ref(3)
const full = ratings.full
const result = computed(() => {
  const mask = ratingsMask(hide.value)
  const f = fit(full, init(full, r.value, 'nndsvd'), 500, 'mu', { mask })
  const Y = mul(f.W, f.H)
  let e = 0, nh = 0, seen = 0, sumSeen = 0
  mask.a.forEach((m, i) => { if (m) { seen++; sumSeen += full.a[i] } })
  const mean = sumSeen / Math.max(seen, 1)
  let eb = 0
  mask.a.forEach((m, i) => {
    if (!m) { nh++; e += Math.abs(Y.a[i] - full.a[i]); eb += Math.abs(mean - full.a[i]) }
  })
  return { mask, Y, seen, nh, err: e / Math.max(nh, 1), base: eb / Math.max(nh, 1) }
})
</script>

<template>
  <div class="wrap">
    <div class="note top">Fill a table with holes</div>
    <div class="body">
      <div class="col">
        <MatView :M="full" :mask="result.mask" ramp="x" :vmin="1" :vmax="5" title="X as observed" title-color="#2b6cb0" />
        <div class="cap">users →, items ↓. {{ result.seen }} of {{ full.a.length }} ratings given</div>
      </div>
      <div class="col">
        <MatView :M="result.Y" ramp="x" :vmin="1" :vmax="5" title="WH, every cell filled" :title-color="GREEN" />
        <div class="cap">error on the {{ result.nh }} hidden ones: <b :style="{ color: GREEN }">{{ result.err.toFixed(2) }} stars</b><br>predicting the mean rating instead: {{ result.base.toFixed(2) }} stars</div>
      </div>
      <div class="side">
        <div class="h" :style="{ color: GOLD }">Trick</div>
        <p>Give the missing cells weight 0: they cost nothing, so they constrain nothing.</p>
        <div class="h" :style="{ color: GREEN }">Prediction</div>
        <Tex formula="\widehat{X}_{ij} = [WH]_{ij}" />
        <p class="note">This is weighted NMF.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="hide" :min="0.05" :max="0.92" :step="0.01" label="share hidden" :color="INK" />
      <Knob v-model="r" :min="1" :max="8" :step="1" label="r" :digits="0" :color="INK" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.body { display: grid; grid-template-columns: 1fr 1fr 14rem; gap: 1.6rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.78rem; line-height: 1.4; }
.side { align-self: center; }
</style>
