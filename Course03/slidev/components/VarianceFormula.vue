<!-- eq_forest_variance: the formula, with both of its symbols given numbers.
     The two terms are drawn as a stacked bar, so which one is the floor is
     something you can see rather than take on faith. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GREEN, MUTED, RED } from '../lib/theme'

const M = ref(100)
const rho = ref(0.2)

const terms = computed(() => {
  const m = Math.round(M.value)
  const indep = 1 / m
  const shared = ((m - 1) / m) * rho.value
  return { indep, shared, total: indep + shared }
})
</script>

<template>
  <div class="box">
    <div class="bars">
      <div class="bar">
        <div class="seg indep" :style="{ width: `${terms.indep * 100}%` }">
          <span v-if="terms.indep > 0.08">σ²/M</span>
        </div>
        <div class="seg shared" :style="{ width: `${terms.shared * 100}%` }">
          <span v-if="terms.shared > 0.1">(M−1)/M · ρσ²</span>
        </div>
      </div>
      <div class="scale"><span>0</span><span>σ², the variance of one tree</span></div>
    </div>
    <div class="knobs">
      <Knob v-model="M" :min="1" :max="1000" :step="1" log label="trees, M" :digits="0" :color="GREEN" />
      <Knob v-model="rho" :min="0" :max="0.9" label="correlation, ρ" :digits="2" :color="RED" />
      <Readout
        :items="[
          { label: 'σ²/M', value: terms.indep.toFixed(3), color: GREEN },
          { label: 'ρ term', value: terms.shared.toFixed(3), color: RED },
          { label: 'total, in units of σ²', value: terms.total.toFixed(3) },
        ]"
      />
    </div>
    <div class="cols">
      <div>
        <h4 :style="{ color: GREEN }">σ² : refit one tree on a fresh sample</h4>
        <p class="note">How far does its prediction jump? Divided by M, so it vanishes.</p>
      </div>
      <div>
        <h4 :style="{ color: RED }">ρ : take two trees of the forest</h4>
        <p class="note">Do they get the same rows wrong? Divided by nothing.</p>
      </div>
    </div>
    <p class="note center">
      Deep unstable trees make σ² big; trees grown on the same rows and the same
      columns make ρ big.
    </p>
  </div>
</template>

<style scoped>
.box { display: flex; flex-direction: column; gap: 0.9rem; }
.bar {
  display: flex; height: 2.2rem; border: 1px solid var(--grid); border-radius: 0.25rem;
  overflow: hidden; background: #fbfbfc;
}
.seg { display: flex; align-items: center; justify-content: center; font-size: 0.78rem; color: white; font-weight: 600; }
.indep { background: #00ab0e; }
.shared { background: #c53030; }
.scale { display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--muted); margin-top: 0.2rem; }
.knobs { display: flex; gap: 2rem; align-items: center; flex-wrap: wrap; }
.knobs > :first-child, .knobs > :nth-child(2) { min-width: 12rem; }
.note { font-size: 0.8rem; color: var(--muted); margin: 0.1rem 0; }
.center { text-align: center; }
h4 { margin: 0; font-size: 0.9rem; }
</style>
