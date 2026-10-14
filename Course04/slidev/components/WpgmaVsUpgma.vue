<!-- wpgma / wpgma_vs_upgma: "weighted" means the two children count equally,
     which is exactly when it differs from counting the points. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { GOLD, GREEN, MUTED, PURPLE } from '../lib/theme'

const na = ref(2)
const nb = ref(20)
const da = ref(1)
const db = ref(5)

const wpgma = computed(() => (da.value + db.value) / 2)
const upgma = computed(() => (na.value * da.value + nb.value * db.value) / (na.value + nb.value))
const gap = computed(() => Math.abs(wpgma.value - upgma.value))
/** how the two answers move as C_b grows, with everything else held */
const curve = computed(() =>
  Array.from({ length: 60 }, (_, i) => {
    const n = 1 + i * 2
    return [n, (na.value * da.value + n * db.value) / (na.value + n)] as [number, number]
  }),
)
</script>

<template>
  <div class="wrap">
    <div class="left">
      <div class="heads">
        <div :style="{ color: PURPLE }"><strong>WPGMA</strong> weighted pair group method with arithmetic mean</div>
        <div :style="{ color: GOLD }"><strong>UPGMA</strong> unweighted pair group method with arithmetic mean</div>
        <div class="note">"weighted" means the two children count equally, not
          that their sizes count.</div>
      </div>
      <div class="diagram">
        <div class="col">
          <div class="box" :style="{ borderColor: PURPLE, color: PURPLE }">C<sub>a</sub>: {{ na }} points</div>
          <div class="box" :style="{ borderColor: PURPLE, color: PURPLE }">C<sub>b</sub>: {{ nb }} points</div>
        </div>
        <div class="dists">
          <div :style="{ color: MUTED }">D = {{ da.toFixed(1) }} ↘</div>
          <div :style="{ color: MUTED }">D = {{ db.toFixed(1) }} ↗</div>
        </div>
        <div class="box" :style="{ borderColor: GOLD, color: GOLD }">C<sub>j</sub></div>
      </div>
      <div class="controls">
        <Knob v-model="na" :min="1" :max="60" :step="1" label="points in C<sub>a</sub>" :digits="0" :color="PURPLE" />
        <Knob v-model="nb" :min="1" :max="60" :step="1" label="points in C<sub>b</sub>" :digits="0" :color="PURPLE" />
        <Knob v-model="da" :min="0.2" :max="8" label="D(C<sub>a</sub>, C<sub>j</sub>)" :color="MUTED" />
        <Knob v-model="db" :min="0.2" :max="8" label="D(C<sub>b</sub>, C<sub>j</sub>)" :color="MUTED" />
      </div>
    </div>
    <div class="right">
      <div class="results">
        <div class="res">
          <div :style="{ color: PURPLE }"><strong>WPGMA</strong></div>
          <div class="eq">({{ da.toFixed(1) }} + {{ db.toFixed(1) }}) / 2</div>
          <div class="big" :style="{ color: PURPLE }">{{ wpgma.toFixed(2) }}</div>
          <div class="note">each child gets half a vote</div>
        </div>
        <div class="res">
          <div :style="{ color: GOLD }"><strong>UPGMA</strong></div>
          <div class="eq">({{ na }}·{{ da.toFixed(1) }} + {{ nb }}·{{ db.toFixed(1) }}) / {{ na + nb }}</div>
          <div class="big" :style="{ color: GOLD }">{{ upgma.toFixed(2) }}</div>
          <div class="note">each point gets a vote</div>
        </div>
      </div>
      <LineChart
        :series="[{ points: curve, color: GOLD, width: 2.4 }]"
        :hlines="[{ y: wpgma, color: PURPLE, dash: '6,4' }]"
        :dots="[{ x: nb, y: upgma, color: GOLD, r: 5 }]"
        :vlines="[{ x: nb, color: GOLD, dash: '' }]"
        :labels="[{ x: 62, y: wpgma + 0.2, text: 'WPGMA, flat', color: PURPLE, size: 11 }]"
        :x-domain="[1, 119]" :y-domain="[Math.min(da, db) - 0.3, Math.max(da, db) + 0.3]"
        :x-ticks="[1, 40, 80, 119]"
        x-label="points in C_b" y-label="distance to C_j"
        title="UPGMA follows the bigger child; WPGMA does not" :title-color="GOLD"
      />
      <Readout
        :items="[
          { label: 'difference', value: gap.toFixed(2), color: gap > 0.5 ? GOLD : GREEN },
          { label: 'they agree when', value: na === nb ? 'the sizes are equal: now' : 'the two sizes are equal' },
        ]"
      />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1fr 1.08fr; gap: 1.6rem; height: 100%; min-height: 0; }
.left { display: flex; flex-direction: column; gap: 0.7rem; justify-content: center; }
.right { display: grid; grid-template-rows: auto 1fr auto; gap: 0.4rem; min-height: 0; }
.heads { font-size: 0.82rem; line-height: 1.6; }
.diagram { display: flex; align-items: center; gap: 0.9rem; font-size: 0.78rem; }
.col { display: flex; flex-direction: column; gap: 0.35rem; }
.dists { display: flex; flex-direction: column; gap: 0.5rem; font-size: 0.75rem; }
.box { border: 1.8px solid; border-radius: 0.3rem; padding: 0.16rem 0.45rem; white-space: nowrap; }
.controls { display: grid; grid-template-columns: 1fr 1fr; gap: 0.35rem 1rem; }
.results { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; }
.res { font-size: 0.8rem; }
.eq { color: #9aa0a6; font-size: 0.76rem; margin: 0.15rem 0; }
.big { font-size: 1.45rem; font-weight: 600; font-variant-numeric: tabular-nums; }
</style>
