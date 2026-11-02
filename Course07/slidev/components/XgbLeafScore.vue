<!-- xgb_leaf_score: substitute w* back and the leaf stops being an unknown.
     What is left is a score of a SET OF ROWS, and a split is judged by how
     much score it buys minus what the extra leaf costs. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { gainOf, score, splitDemo } from '../lib/gbm'
import { BLUE, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const cut = ref(0.53)
const lambda = ref(1)
const gamma = ref(0.5)
const demo = splitDemo()

const node = computed(() => {
  let GL = 0, HL = 0, G = 0, H = 0, nL = 0
  for (let i = 0; i < demo.X.length; i++) {
    G += demo.g[i]
    H += demo.h[i]
    if (demo.X[i][0] < cut.value) {
      GL += demo.g[i]
      HL += demo.h[i]
      nL++
    }
  }
  const GR = G - GL
  const HR = H - HL
  return {
    G, H, GL, HL, GR, HR, nL, nR: demo.X.length - nL,
    sL: score(GL, HL, lambda.value),
    sR: score(GR, HR, lambda.value),
    sN: score(G, H, lambda.value),
    gain: gainOf(GL, HL, GR, HR, lambda.value, gamma.value),
  }
})
</script>

<template>
  <div class="wrap">
    <div class="steps">
      <div class="step">
        <p class="cap">the objective, restricted to one leaf j</p>
        <p class="formula" :style="{ color: MUTED }">Gⱼw + ½(Hⱼ + λ)w² + γ</p>
      </div>
      <span class="arrow">→</span>
      <div class="step">
        <p class="cap">a quadratic in w, so its minimum is closed-form</p>
        <p class="formula" :style="{ color: PURPLE }">wⱼ* = − Gⱼ / (Hⱼ + λ)</p>
      </div>
      <span class="arrow">→</span>
      <div class="step">
        <p class="cap">and its value THERE is a number, with no w left</p>
        <p class="formula" :style="{ color: BLUE }">− ½ Gⱼ² / (Hⱼ + λ) + γ</p>
      </div>
    </div>
    <p class="score">s(G, H) = G² / (H + λ) &nbsp; is the score of a set of rows</p>
    <div class="gainbox" :style="{ borderColor: node.gain > 0 ? GREEN : RED }">
      <span class="gf">gain = ½ [ s(G<sub>L</sub>,H<sub>L</sub>) + s(G<sub>R</sub>,H<sub>R</sub>) − s(G,H) ] − γ</span>
      <span class="gn">
        = ½ [ {{ node.sL.toFixed(2) }} + {{ node.sR.toFixed(2) }} − {{ node.sN.toFixed(2) }} ] − {{ gamma.toFixed(2) }}
        = <b :style="{ color: node.gain > 0 ? GREEN : RED }">{{ node.gain.toFixed(2) }}</b>
      </span>
    </div>
    <div class="knobs">
      <Knob v-model="cut" :min="0.05" :max="0.95" label="candidate split x₁ &lt;" :digits="2" />
      <Knob v-model="lambda" :min="0.01" :max="100" log label="λ" :color="PURPLE" />
      <Knob v-model="gamma" :min="0" :max="8" label="γ" :digits="2" :color="RED" />
      <Readout
        :items="[
          { label: 'rows', value: `${node.nL} | ${node.nR}` },
          { label: 'verdict', value: node.gain > 0 ? 'split it' : 'leave it a leaf', color: node.gain > 0 ? GREEN : RED },
        ]"
      />
    </div>
    <p class="note">
      A candidate split is one (feature, threshold) pair; the node takes the one with
      the largest gain, and stays a leaf if no candidate gets the gain above zero.
    </p>
  </div>
</template>

<style scoped>
.wrap { display: flex; flex-direction: column; justify-content: center; gap: 0.8rem; height: 100%; }
.steps { display: grid; grid-template-columns: 1fr auto 1fr auto 1fr; gap: 0 0.6rem; align-items: center; }
.step { text-align: center; }
.cap { font-size: 0.78rem; color: var(--muted); margin: 0 0 0.3rem; line-height: 1.4; }
.formula { font-size: 1rem; margin: 0; }
.arrow { color: var(--muted); }
.score { text-align: center; font-size: 0.95rem; margin: 0; }
.gainbox {
  border: 2px solid; border-radius: 0.4rem; padding: 0.5rem 0.8rem;
  display: flex; flex-direction: column; align-items: center; gap: 0.25rem;
}
.gf { font-size: 0.95rem; }
.gn { font-size: 0.9rem; font-variant-numeric: tabular-nums; color: #3a3a3a; }
.knobs { display: flex; gap: 1.6rem; align-items: center; flex-wrap: wrap; }
.knobs > :nth-child(-n+3) { min-width: 10rem; }
.note { font-size: 0.78rem; color: var(--muted); margin: 0; text-align: center; }
</style>
