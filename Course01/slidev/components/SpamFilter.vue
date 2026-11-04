<!-- spam_filter: naive Bayes on a bag of words. Tick the words the e-mail
     contains; the score is log πₖ + Σ log fₖ(word). -->
<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { BLUE, GREEN, INK, RED } from '../lib/theme'

const WORDS = ['free', 'meeting', 'click', 'report', 'winner']
const SPAM = [0.031, 0.002, 0.024, 0.003, 0.018]
const HAM = [0.004, 0.019, 0.002, 0.022, 0.001]
const on = reactive([true, false, true, false, false])
const pi = ref(0.3)
const terms = computed(() => WORDS.map((w, j) => ({ w, s: Math.log(SPAM[j]), h: Math.log(HAM[j]), on: on[j] })))
const ls = computed(() => Math.log(pi.value) + terms.value.reduce((a, t) => a + (t.on ? t.s : 0), 0))
const lh = computed(() => Math.log(1 - pi.value) + terms.value.reduce((a, t) => a + (t.on ? t.h : 0), 0))
const pSpam = computed(() => 1 / (1 + Math.exp(lh.value - ls.value)))
</script>

<template>
  <div class="cmp">
    <div class="r2" style="align-items: center">
      <div class="side">
        <div class="h" :style="{ color: BLUE }">bag of words</div>
        <p>xⱼ = how often word j occurs; d = size of the dictionary</p>
        <p :style="{ color: RED }">fₖ(xⱼ): frequency of word j in class k</p>
        <p :style="{ color: RED }">πₖ: share of spam in the mailbox</p>
        <p style="margin-top: 0.8rem"><Tex formula="\hat C(x) = \arg\max_k\ \pi_k \prod_j f_k(x_j)" /></p>
        <p style="margin-top: 0.8rem; font-weight: 700" :style="{ color: GREEN }">→ basically counting words</p>
      </div>
      <table class="plain spam">
        <thead><tr><th>in the e-mail?</th><th>word</th><th :style="{ color: RED }">spam</th><th :style="{ color: BLUE }">normal</th></tr></thead>
        <tbody>
          <tr v-for="(t, j) in terms" :key="t.w" :class="{ off: !t.on }">
            <td><input type="checkbox" v-model="on[j]" /></td>
            <td>{{ t.w }}</td>
            <td :style="{ color: RED }">{{ SPAM[j].toFixed(3) }}</td>
            <td :style="{ color: BLUE }">{{ HAM[j].toFixed(3) }}</td>
          </tr>
          <tr class="sum"><td></td><td>log πₖ + Σ log fₖ</td><td :style="{ color: RED }">{{ ls.toFixed(1) }}</td><td :style="{ color: BLUE }">{{ lh.toFixed(1) }}</td></tr>
        </tbody>
      </table>
    </div>
    <div class="foot">P(spam | e-mail) = <b :style="{ color: pSpam > 0.5 ? RED : BLUE }">{{ (100 * pSpam).toFixed(1) }}%</b>: classified as <b :style="{ color: pSpam > 0.5 ? RED : BLUE }">{{ pSpam > 0.5 ? 'spam' : 'normal' }}</b>. Each word multiplies the odds by f<sub>spam</sub> / f<sub>normal</sub>, whatever the other words are.</div>
    <div class="controls"><Knob v-model="pi" :min="0.01" :max="0.99" :step="0.01" label="share of spam π<sub>spam</sub>" :color="RED" /></div>
  </div>
</template>

<style scoped>
.spam { font-size: 0.95rem; }
.spam td, .spam th { text-align: center; }
.spam tr.off td:not(:first-child) { opacity: 0.35; }
.spam tr.sum td { border-top: 1px solid #cccfd2; font-weight: 600; color: #1b1b1b; }
.spam input { width: 1rem; height: 1rem; accent-color: #1b1b1b; cursor: pointer; }
</style>
