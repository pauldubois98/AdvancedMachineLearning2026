<!-- mreach_example: six points, three pairs, one table. The slider is k, and
     which of the three numbers wins the max changes with it. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { distances, mreachToy } from '../lib/data4'
import { coreDistances } from '../lib/density'
import { GOLD, GREEN, INK, MUTED, RED } from '../lib/theme'

const k = ref(2)
const { X, names } = mreachToy()
const D = distances(X)
const core = computed(() => coreDistances(X, k.value, D))
const pairs = [
  { i: 0, j: 1, why: 'both in the crowd', color: GREEN },
  { i: 1, j: 4, why: 'one of them alone', color: GOLD },
  { i: 4, j: 5, why: 'both out at sea', color: RED },
]
const rows = computed(() =>
  pairs.map((p) => {
    const vals = [D[p.i][p.j], core.value[p.i], core.value[p.j]]
    const best = vals.indexOf(Math.max(...vals))
    return { ...p, vals, best, mreach: Math.max(...vals) }
  }),
)
</script>

<template>
  <div class="wrap">
    <ClusterPlot
      :X="X" :point-size="4.5" :colors="X.map(() => INK)" :domain="[-1.4, 3.6, -1.4, 2.4]"
      :circles="[0, 4, 5].map((i) => ({ x: X[i][0], y: X[i][1], r: core[i], color: i === 0 ? '#2b6cb0' : RED, alpha: 0.05, dash: [5, 4] }))"
      :tags="names.map((nm, i) => ({ x: X[i][0] + 0.13, y: X[i][1] + 0.14, text: nm, size: 12, anchor: 'left' as CanvasTextAlign }))"
      :title="`dashed circles are core<sub>${k}</sub>`"
    />
    <div class="right">
      <div class="formula">
        <Tex display formula='d_{\text{mreach}}(x_i, x_j) = \max\left(\text{core}_k(x_i),\ \text{core}_k(x_j),\ d(x_i, x_j)\right)' />
      </div>
      <table class="plain narrow">
        <tr>
          <th>pair</th><th>d</th><th>core(first)</th><th>core(second)</th><th>d<sub>mreach</sub></th>
        </tr>
        <tr v-for="r in rows" :key="`${r.i}${r.j}`">
          <td :style="{ color: INK }">{{ names[r.i] }}, {{ names[r.j] }}</td>
          <td
            v-for="(v, c) in r.vals" :key="c"
            :style="{ color: c === r.best ? r.color : MUTED, fontWeight: c === r.best ? 600 : 400 }"
          >{{ v.toFixed(2) }}</td>
          <td :style="{ color: r.color, fontWeight: 600 }">{{ r.mreach.toFixed(2) }}</td>
        </tr>
      </table>
      <div class="whys">
        <span v-for="r in rows" :key="`w${r.i}`" class="note" :style="{ color: r.color }">
          {{ names[r.i] }},{{ names[r.j] }}: {{ r.why }}
        </span>
      </div>
      <Knob v-model="k" :min="1" :max="5" :step="1" label="k" :digits="0" :color="GREEN" />
      <Readout
        :items="[
          { label: 'A,B inflated by', value: (rows[0].mreach - rows[0].vals[0]).toFixed(2), color: GREEN },
          { label: 'P,Q inflated by', value: (rows[2].mreach - rows[2].vals[0]).toFixed(2), color: RED },
        ]"
      />
      <p class="note">Inside the crowd the three numbers are all of a size, so
        d<sub>mreach</sub> barely moves: A and B are pushed apart by a few
        hundredths. Every pair that touches P or Q is pushed much further,
        because the max is then a core distance and not d at all. Raise k and
        watch the crowd start to feel it too.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 0.9fr 1.15fr; gap: 1.5rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; gap: 0.5rem; justify-content: center; }
.formula { font-size: 0.8rem; }
.whys { display: flex; gap: 1rem; flex-wrap: wrap; }
</style>
