<!-- linkage_update: after a merge, every other distance has to be rebuilt, and
     each linkage is just four numbers in the same update rule. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GOLD, GREEN, INK, PURPLE, RED } from '../lib/theme'

const daj = ref(3.0)
const dbj = ref(5.0)
const dab = ref(2.0)
const na = ref(2)
const nb = ref(20)
const nj = ref(8)

const rules = computed(() => [
  { key: 'single', name: 'single', color: BLUE, aa: 0.5, ab: 0.5, beta: 0, gamma: -0.5 },
  { key: 'complete', name: 'complete', color: RED, aa: 0.5, ab: 0.5, beta: 0, gamma: 0.5 },
  { key: 'weighted', name: 'WPGMA', color: PURPLE, aa: 0.5, ab: 0.5, beta: 0, gamma: 0 },
  {
    key: 'average', name: 'UPGMA', color: GOLD,
    aa: na.value / (na.value + nb.value), ab: nb.value / (na.value + nb.value), beta: 0, gamma: 0,
  },
])
const results = computed(() =>
  rules.value.map((r) => ({
    ...r,
    value: r.aa * daj.value + r.ab * dbj.value + r.beta * dab.value + r.gamma * Math.abs(daj.value - dbj.value),
  })),
)
/** Ward needs the sizes, so it is written out rather than squeezed into the row */
const ward = computed(() => {
  const { value: na_ } = na
  const nbv = nb.value
  const njv = nj.value
  return Math.sqrt(
    ((na_ + njv) * daj.value ** 2 + (nbv + njv) * dbj.value ** 2 - njv * dab.value ** 2) /
      (na_ + nbv + njv),
  )
})
</script>

<template>
  <div class="wrap">
    <div class="left">
      <div class="diagram">
        <div class="col">
          <div class="box" :style="{ borderColor: PURPLE, color: PURPLE }">C<sub>a</sub> (n = {{ na }})</div>
          <div class="box" :style="{ borderColor: PURPLE, color: PURPLE }">C<sub>b</sub> (n = {{ nb }})</div>
        </div>
        <div class="arrow">→</div>
        <div class="box wide" :style="{ borderColor: PURPLE, color: PURPLE }">C<sub>i</sub> = C<sub>a</sub> ∪ C<sub>b</sub></div>
        <div class="link">
          <span class="q" :style="{ color: GOLD }">?</span>
        </div>
        <div class="box" :style="{ borderColor: GOLD, color: GOLD }">C<sub>j</sub> (n = {{ nj }})</div>
      </div>
      <div class="formula">
        <Tex display formula='D(C_i, C_j) = \alpha_a D(C_a, C_j) + \alpha_b D(C_b, C_j) + \beta D(C_a, C_b) + \gamma\,|D(C_a, C_j) - D(C_b, C_j)|' />
      </div>
      <p class="note">Everything on the right is already known before the merge,
        so a linkage is a choice of four numbers, not a new pass over the points.</p>
      <div class="controls">
        <Knob v-model="daj" :min="0.2" :max="8" label="D(C<sub>a</sub>, C<sub>j</sub>)" :color="INK" />
        <Knob v-model="dbj" :min="0.2" :max="8" label="D(C<sub>b</sub>, C<sub>j</sub>)" :color="INK" />
        <Knob v-model="dab" :min="0.2" :max="8" label="D(C<sub>a</sub>, C<sub>b</sub>)" :color="INK" />
        <Knob v-model="na" :min="1" :max="60" :step="1" label="n<sub>a</sub>" :digits="0" :color="PURPLE" />
        <Knob v-model="nb" :min="1" :max="60" :step="1" label="n<sub>b</sub>" :digits="0" :color="PURPLE" />
        <Knob v-model="nj" :min="1" :max="60" :step="1" label="n<sub>j</sub>" :digits="0" :color="GOLD" />
      </div>
    </div>
    <div class="right">
      <table class="plain narrow">
        <tr>
          <th>linkage</th><th>α<sub>a</sub></th><th>α<sub>b</sub></th><th>β</th><th>γ</th>
          <th>D(C<sub>i</sub>, C<sub>j</sub>)</th>
        </tr>
        <tr v-for="r in results" :key="r.key">
          <td :style="{ color: r.color, fontWeight: 600 }">{{ r.name }}</td>
          <td>{{ r.aa.toFixed(2) }}</td>
          <td>{{ r.ab.toFixed(2) }}</td>
          <td>{{ r.beta.toFixed(0) }}</td>
          <td>{{ r.gamma.toFixed(1) }}</td>
          <td :style="{ color: r.color, fontWeight: 600 }">{{ r.value.toFixed(2) }}</td>
        </tr>
        <tr>
          <td :style="{ color: GREEN, fontWeight: 600 }">Ward</td>
          <td colspan="4" class="note">needs n<sub>a</sub>, n<sub>b</sub>, n<sub>j</sub></td>
          <td :style="{ color: GREEN, fontWeight: 600 }">{{ ward.toFixed(2) }}</td>
        </tr>
      </table>
      <Readout
        :items="[
          { label: 'single picks', value: Math.min(daj, dbj).toFixed(2), color: BLUE },
          { label: 'complete picks', value: Math.max(daj, dbj).toFixed(2), color: RED },
          { label: 'spread between the linkages', value: (Math.max(...results.map((r) => r.value), ward) - Math.min(...results.map((r) => r.value), ward)).toFixed(2) },
        ]"
      />
      <p class="note">Move the two known distances apart and the linkages
        disagree more: they only ever coincide when D(C<sub>a</sub>, C<sub>j</sub>)
        = D(C<sub>b</sub>, C<sub>j</sub>), and the sizes only matter to UPGMA and
        Ward.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.05fr 1fr; gap: 1.6rem; height: 100%; min-height: 0; }
.left { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.right { display: flex; flex-direction: column; gap: 0.6rem; justify-content: center; }
.diagram { display: flex; align-items: center; gap: 0.5rem; font-size: 0.78rem; }
.col { display: flex; flex-direction: column; gap: 0.3rem; }
.box { border: 1.8px solid; border-radius: 0.3rem; padding: 0.16rem 0.45rem; white-space: nowrap; }
.box.wide { font-weight: 600; }
.arrow { color: #9aa0a6; }
.link { flex: 1 1 auto; border-top: 1.6px solid #b7791f; position: relative; height: 1px; }
.q { position: absolute; left: 50%; top: -1.1rem; transform: translateX(-50%); font-weight: 700; }
.formula { font-size: 0.8rem; }
.controls { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.3rem 0.9rem; }
</style>
