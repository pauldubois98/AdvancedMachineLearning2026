<!-- weighted_idea: X and its matrix of weights Σ, here a mask: 1 where an
     entry is observed, 0 elsewhere. Slide the share observed. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { mat } from '../lib/mat'
import { Rng } from '../lib/rng'
import { BLUE, GOLD, INK, PURPLE } from '../lib/theme'

const share = ref(0.55)
const R = 11, C = 15
const X = (() => { const m = mat(R, C); const rng = new Rng(4); for (let i = 0; i < m.a.length; i++) m.a[i] = rng.next() ** 1.6; return m })()
const u = (() => { const rng = new Rng(9); return Float64Array.from({ length: R * C }, () => rng.next()) })()
const S = computed(() => ({ r: R, c: C, a: Float64Array.from(u, (v) => (v < share.value ? 1 : 0)) }))
</script>

<template>
  <div class="wrap">
    <div class="body">
      <div class="col">
        <MatView :M="X" :mask="S" ramp="x" :border="BLUE" title="X" :title-color="BLUE" square />
        <div class="cap">grey = not observed</div>
      </div>
      <div class="col">
        <MatView :M="S" ramp="w" :vmax="1" :border="PURPLE" title="Σ" :title-color="PURPLE" square />
        <div class="cap">1 where observed, 0 elsewhere</div>
      </div>
      <div class="side">
        <div class="h" :style="{ color: GOLD }">Why weight</div>
        <p>— entries not observed</p>
        <p>— entries trusted less</p>
        <p>— an outlier to ignore</p>
        <p>— a class more important</p>
        <p class="note">Σ does not need to be binary.</p>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="share" :min="0" :max="1" :step="0.01" label="share observed" :color="INK" />
      <span class="note">Missing entries are predicted by WH.</span>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: 1fr auto; gap: 0.4rem; height: 100%; min-height: 0; }
.body { display: grid; grid-template-columns: 1fr 1fr 14rem; gap: 2rem; min-height: 0; }
.col { display: grid; grid-template-rows: 1fr auto; gap: 0.3rem; min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.8rem; }
.side { align-self: center; }
</style>
