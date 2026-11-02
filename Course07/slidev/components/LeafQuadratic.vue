<!-- eq_leaf_objective: every leaf sits in its own term, so the sum splits into
     T independent problems, each one quadratic in a single unknown. Move G, H
     and lambda and watch where the parabola's bottom goes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { leafValue, score } from '../lib/gbm'
import { BLUE, GREEN, INK, MUTED, PURPLE, RED } from '../lib/theme'

const G = ref(-3)
const H = ref(4)
const lambda = ref(1)

const curve = computed(() => {
  const pts: [number, number][] = []
  for (let i = 0; i <= 240; i++) {
    const w = -4 + (8 * i) / 240
    pts.push([w, G.value * w + 0.5 * (H.value + lambda.value) * w * w])
  }
  return pts
})
const wStar = computed(() => leafValue(G.value, H.value, lambda.value))
const objStar = computed(() => -0.5 * score(G.value, H.value, lambda.value))
const noReg = computed(() => leafValue(G.value, H.value, 0))
</script>

<template>
  <div class="wrap">
    <LineChart
      :series="[{ points: curve, color: INK, width: 2.4 }]"
      :dots="[
        { x: wStar, y: objStar, color: GREEN, r: 6 },
        { x: noReg, y: G * noReg + 0.5 * H * noReg * noReg, color: MUTED, r: 4, hollow: true },
      ]"
      :vlines="[{ x: wStar, color: GREEN, dash: '3,3' }, { x: 0, color: MUTED, dash: '' }]"
      :hlines="[{ y: 0, color: MUTED, dash: '' }]"
      :x-domain="[-4, 4]" :y-domain="[-6, 14]"
      :x-ticks="[-4, -2, 0, 2, 4]" :y-ticks="[-5, 0, 5, 10]"
      x-label="the value this leaf outputs, w" y-label="objⱼ(w)"
      title="one quadratic, one unknown"
      :labels="[
        { x: wStar + 0.12, y: objStar - 1.2, text: `w* = ${wStar.toFixed(2)}`, color: GREEN, size: 12 },
        { x: -3.9, y: 13, text: 'grey ring: where the minimum would be with λ = 0', color: MUTED, size: 11 },
      ]"
    />
    <div class="right">
      <p class="eq">objⱼ(w) = G<sub>j</sub> w + ½ (H<sub>j</sub> + λ) w²</p>
      <p class="eq green">w<sub>j</sub>* = − G<sub>j</sub> / (H<sub>j</sub> + λ)</p>
      <p class="eq blue">objⱼ(w*) = − ½ G<sub>j</sub>² / (H<sub>j</sub> + λ)</p>
      <div class="knobs">
        <Knob v-model="G" :min="-8" :max="8" label="Gⱼ = Σ gᵢ in the leaf" :digits="2" :color="BLUE" />
        <Knob v-model="H" :min="0.1" :max="12" label="Hⱼ = Σ hᵢ in the leaf" :digits="2" :color="PURPLE" />
        <Knob v-model="lambda" :min="0" :max="20" label="λ" :digits="2" :color="RED" />
      </div>
      <Readout
        :items="[
          { label: 'w*', value: wStar.toFixed(3), color: GREEN },
          { label: 'its value there', value: objStar.toFixed(3), color: BLUE },
          { label: 'λ pulled it in by', value: (Math.abs(noReg) - Math.abs(wStar)).toFixed(3), color: RED },
        ]"
      />
      <p class="note">
        λ sits beside H in the denominator: a leaf holding few rows has a small H, so
        λ dominates it and its value is pulled hard toward zero, while a leaf holding
        many rows barely notices. That is what "regularisation inside the tree" means.
      </p>
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-columns: 1.1fr 0.95fr; gap: 1.6rem; height: 100%; min-height: 0; }
.right { display: flex; flex-direction: column; justify-content: center; gap: 0.45rem; }
.eq { font-size: 1rem; margin: 0; }
.green { color: var(--green); }
.blue { color: var(--blue); }
.knobs { display: flex; flex-direction: column; gap: 0.3rem; margin-top: 0.4rem; }
.note { font-size: 0.78rem; color: var(--muted); margin: 0.2rem 0 0; line-height: 1.5; }
</style>
