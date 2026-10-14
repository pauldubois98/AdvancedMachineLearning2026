<!-- hamming_distance: count the columns where two rows disagree. Click a
     letter in the second row to change it and watch the count follow. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GREEN, MUTED, RED } from '../lib/theme'

const top = 'GATTACAGTC'.split('')
const bottom = ref('GACTACAGTG'.split(''))
const alphabet = ['A', 'C', 'G', 'T']

const diff = computed(() => top.map((u, i) => u !== bottom.value[i]))
const count = computed(() => diff.value.filter(Boolean).length)

function cycle(i: number) {
  const next = alphabet[(alphabet.indexOf(bottom.value[i]) + 1) % 4]
  bottom.value = bottom.value.map((c, j) => (j === i ? next : c))
}
function reset() {
  bottom.value = 'GACTACAGTG'.split('')
}
function match() {
  bottom.value = [...top]
}
</script>

<template>
  <div class="wrap">
    <div class="strings">
      <div class="row">
        <span class="lab" :style="{ color: BLUE }">x</span>
        <span
          v-for="(c, i) in top" :key="`t${i}`" class="cell"
          :class="{ hit: diff[i] }" :style="{ color: diff[i] ? RED : BLUE }"
        >{{ c }}</span>
      </div>
      <div class="row">
        <span class="lab" :style="{ color: GREEN }">y</span>
        <button
          v-for="(c, i) in bottom" :key="`b${i}`" class="cell button"
          :class="{ hit: diff[i] }" :style="{ color: diff[i] ? RED : GREEN }"
          @click="cycle(i)"
        >{{ c }}</button>
      </div>
      <div class="row">
        <span class="lab small">differs?</span>
        <span
          v-for="(hit, i) in diff" :key="`d${i}`" class="cell small"
          :style="{ color: hit ? RED : MUTED }"
        >{{ hit ? 1 : 0 }}</span>
        <span class="sum" :style="{ color: RED }">= {{ count }}</span>
      </div>
      <div class="note mt-2">click a letter of y: it steps through A, C, G, T</div>
    </div>
    <div class="formula">
      <p><Tex display formula='d_H(x, y) = \sum_{j=1}^{d} \mathbb{1}\left[x_j \neq y_j\right]' /></p>
      <p class="lead">"count the columns where two rows disagree"</p>
      <div class="row gap">
        <button class="plain-btn" @click="reset">back to the example</button>
        <button class="plain-btn" @click="match">make them equal</button>
      </div>
      <Readout
        class="mt-3"
        :items="[
          { label: 'columns', value: String(top.length) },
          { label: 'disagreements', value: String(count), color: RED },
          { label: 'normalised', value: (count / top.length).toFixed(2) },
        ]"
      />
      <p class="note mt-3">text, DNA, survey answers, one-hot features: the
        distance never looks at how far apart two letters are, only whether they
        are the same.</p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 1fr; gap: 2rem; height: 100%; min-height: 0; align-items: center; }
.strings { display: flex; flex-direction: column; gap: 0.35rem; }
.row { display: flex; align-items: center; gap: 0.1rem; }
.row.gap { gap: 0.6rem; margin-top: 0.8rem; }
.lab { width: 3.6rem; text-align: right; padding-right: 0.6rem; font-size: 1rem; }
.lab.small { font-size: 0.78rem; color: #9aa0a6; }
.cell {
  width: 1.6rem; text-align: center; font-size: 1.15rem; font-weight: 600;
  padding: 0.1rem 0; border-radius: 0.2rem;
}
.cell.small { font-size: 0.8rem; font-weight: 400; }
.cell.hit { background: rgba(197, 48, 48, 0.1); }
.button { border: none; background: none; cursor: pointer; font-family: inherit; }
.button:hover { background: rgba(0, 0, 0, 0.06); }
.sum { margin-left: 0.6rem; font-size: 0.95rem; font-weight: 600; }
.formula { font-size: 0.9rem; }
.plain-btn {
  border: 1px solid #d8dadd; border-radius: 0.3rem; padding: 0.16rem 0.5rem;
  background: white; cursor: pointer; font-size: 0.8rem;
}
.plain-btn:hover { border-color: #9aa0a6; }
</style>
