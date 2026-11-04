<!-- laplace_smoothing: one word never seen in a class vetoes the class;
     α added to every count gives it a small head start. -->
<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { BLUE, GREEN, RED } from '../lib/theme'

const WORDS = ['free', 'meeting', 'click', 'report', 'winner']
const NS = [31, 0, 24, 3, 18] // counts in the spam training e-mails
const NH = [4, 19, 2, 22, 1] // counts in the normal ones
const alpha = ref(0)
const on = reactive([true, true, true, false, true])
const d = WORDS.length
const tot = (c: number[]) => c.reduce((a, b) => a + b, 0)
const f = (c: number[], j: number) => (c[j] + alpha.value) / (tot(c) + alpha.value * d)
const score = (c: number[]) => Math.log(0.5) + WORDS.reduce((s, _, j) => s + (on[j] ? Math.log(f(c, j)) : 0), 0)
const pSpam = computed(() => {
  const a = score(NS), b = score(NH)
  if (a === -Infinity && b === -Infinity) return NaN
  if (a === -Infinity) return 0
  return 1 / (1 + Math.exp(b - a))
})
</script>

<template>
  <div class="cmp">
    <div class="r2" style="align-items: center">
      <div class="side">
        <p>what if a word never appeared in a class?</p>
        <p :style="{ color: RED }"><Tex formula="\exists j:\ f_k(x_j) = 0 \;\Longrightarrow\; \prod_j f_k(x_j) = 0" /></p>
        <p :style="{ color: RED }" class="note">one unseen word vetoes the whole class</p>
        <p :style="{ color: GREEN }" style="margin-top: 1rem; font-size: 1.15rem"><Tex formula="\hat f_k(x_j) = \frac{n_{kj} + \alpha}{n_k + \alpha\, d}" /></p>
        <p :style="{ color: GREEN }" class="note">Laplace smoothing: give every word a small head start</p>
      </div>
      <table class="plain lap">
        <thead><tr><th>in the e-mail?</th><th>word</th><th :style="{ color: RED }">n<sub>spam,j</sub></th><th :style="{ color: RED }">f̂<sub>spam</sub></th><th :style="{ color: BLUE }">n<sub>normal,j</sub></th><th :style="{ color: BLUE }">f̂<sub>normal</sub></th></tr></thead>
        <tbody>
          <tr v-for="(w, j) in WORDS" :key="w" :class="{ off: !on[j] }">
            <td><input type="checkbox" v-model="on[j]" /></td>
            <td>{{ w }}</td>
            <td :style="{ color: RED }">{{ NS[j] }}</td>
            <td :style="{ color: RED, fontWeight: f(NS, j) === 0 ? 700 : 400 }">{{ f(NS, j).toFixed(3) }}</td>
            <td :style="{ color: BLUE }">{{ NH[j] }}</td>
            <td :style="{ color: BLUE }">{{ f(NH, j).toFixed(3) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
    <div class="foot">P(spam | e-mail) = <b :style="{ color: RED }">{{ Number.isNaN(pSpam) ? 'undefined (0 / 0)' : (100 * pSpam).toFixed(1) + '%' }}</b>
      <span v-if="alpha === 0 && on[1]"> · "meeting" never appeared in spam, so with α = 0 no e-mail containing it can be spam, however many spam words it has</span>
      <span v-else> · with α &gt; 0 the evidence of the other words counts again</span></div>
    <div class="controls"><Knob v-model="alpha" :min="0" :max="5" :step="0.05" label="smoothing α" :color="GREEN" /></div>
  </div>
</template>

<style scoped>
.lap { font-size: 0.9rem; }
.lap td, .lap th { text-align: center; }
.lap tr.off td:not(:first-child) { opacity: 0.35; }
.lap input { width: 1rem; height: 1rem; accent-color: #1b1b1b; cursor: pointer; }
</style>
