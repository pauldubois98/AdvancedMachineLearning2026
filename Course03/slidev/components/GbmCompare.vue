<!-- gbm_compare: same objective, same gain, same leaf value; everything below
     is a different answer to "how do we afford it". Click a library to read
     its column on its own. -->
<script setup lang="ts">
import { ref } from 'vue'
import { BLUE, GREEN, PURPLE } from '../lib/theme'

const focus = ref('all')
const LIBS = [
  { key: 'xgb', name: 'XGBoost', color: BLUE },
  { key: 'lgbm', name: 'LightGBM', color: GREEN },
  { key: 'cat', name: 'CatBoost', color: PURPLE },
]
const ROWS = [
  { what: 'finding a split', xgb: 'every midpoint, or sketched quantiles', lgbm: '~255 bins, filled in one pass', cat: 'bins, as LightGBM does' },
  { what: 'growing the tree', xgb: 'level-wise, depth-limited', lgbm: 'leaf-wise, num_leaves-limited', cat: 'oblivious: ONE split per level' },
  { what: 'which rows', xgb: 'all', lgbm: 'GOSS', cat: 'a permutation of the rows' },
  { what: 'categoricals', xgb: 'to encode yourself', lgbm: 'greedy target statistics', cat: 'ordered target statistics' },
  { what: 'what it is best at', xgb: 'small data, forgiving defaults', lgbm: 'large tabular data, speed', cat: 'many categoricals, fast inference' },
]
const dim = (k: string) => focus.value !== 'all' && focus.value !== k
</script>

<template>
  <div class="wrap">
    <table class="cmp">
      <thead>
        <tr>
          <th></th>
          <th
            v-for="l in LIBS" :key="l.key"
            :style="{ color: l.color, opacity: dim(l.key) ? 0.25 : 1 }"
          >{{ l.name }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in ROWS" :key="r.what">
          <td class="what">{{ r.what }}</td>
          <td
            v-for="l in LIBS" :key="l.key"
            :style="{ color: l.color, opacity: dim(l.key) ? 0.25 : 1 }"
          >{{ (r as any)[l.key] }}</td>
        </tr>
      </tbody>
    </table>
    <div class="controls">
      <Choice
        v-model="focus" label="read one column"
        :options="[
          { value: 'all', label: 'all three' },
          ...LIBS.map((l) => ({ value: l.key, label: l.name, color: l.color })),
        ]"
      />
      <p class="note">
        the objective, the gain and the leaf value are the same three formulas in all
        three libraries; what differs is how much of the data each one is willing to
        look at, and in what order it spends its splits.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: flex; flex-direction: column; justify-content: center; gap: 1rem; height: 100%; }
.cmp { border-collapse: collapse; width: 100%; font-size: 0.88rem; }
.cmp th {
  text-align: left; font-size: 1rem; font-weight: 600; padding: 0 0.8rem 0.4rem 0;
  border-bottom: 1px solid var(--grid); transition: opacity 0.15s;
}
.cmp td { padding: 0.5rem 0.8rem 0.5rem 0; border-bottom: 1px solid #eef0f2; vertical-align: top; transition: opacity 0.15s; }
.what { color: var(--ink); width: 11rem; }
.controls { display: flex; flex-direction: column; gap: 0.5rem; }
.note { font-size: 0.8rem; color: var(--muted); margin: 0; line-height: 1.5; }
</style>
