<!-- setup_faces: what X, W and H hold for faces. Pick a face (a column of X
     and of H) and a part (a column of W); the bar of that part is outlined. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { SIDE, face, facesNmf } from '../lib/data5'
import { BLUE, GOLD, INK, PURPLE } from '../lib/theme'

const j = ref(6)
const k = ref(2)
const P = SIDE * SIDE
const strip = (v: Float64Array) => ({ r: P, c: 1, a: v })
const xj = computed(() => strip(Float64Array.from(face(j.value))))
const wk = computed(() => strip(Float64Array.from(facesNmf.W[k.value])))
const hj = computed(() => facesNmf.H.map((h) => h[j.value]))
const hMax = computed(() => Math.max(...hj.value) * 1.1)
</script>

<template>
  <div class="wrap">
    <div class="note top">What the three matrices hold, for faces</div>
    <div class="cols">
      <div class="col">
        <div class="h" :style="{ color: BLUE }">a column of X <i>x<sub>j</sub></i></div>
        <div class="pair">
          <Tiles :items="[face(j)]" :side="SIDE" :vmin="0" :vmax="1" />
          <span class="arrow">→</span>
          <div class="strip"><MatView :M="xj" ramp="x" :vmax="1" :border="BLUE" /></div>
        </div>
        <div class="cap">one face = {{ P }} pixel values, written as one tall column</div>
        <div class="foot" :style="{ color: BLUE }">X is {{ P }} × 300: one column per face</div>
      </div>
      <div class="col">
        <div class="h" :style="{ color: PURPLE }">a column of W <i>w<sub>k</sub></i></div>
        <div class="pair">
          <Tiles :items="[facesNmf.W[k]]" :side="SIDE" ramp="grayr" />
          <span class="arrow">→</span>
          <div class="strip"><MatView :M="wk" ramp="w" :border="PURPLE" /></div>
        </div>
        <div class="cap">a part is {{ P }} numbers too, so it is an image as well, but shared by all 300 faces</div>
        <div class="foot" :style="{ color: PURPLE }">W is {{ P }} × r: one column per part</div>
      </div>
      <div class="col">
        <div class="h" :style="{ color: GOLD }">a column of H <i>h<sub>j</sub></i></div>
        <div class="bars">
          <LineChart
            :series="[]"
            :bars="hj.map((v, c) => ({ x: c + 1, y: v, y0: 0, w: 0.7, color: GOLD, alpha: c === k ? 1 : 0.45 }))"
            :x-domain="[0.3, 16.7]" :y-domain="[0, hMax]" :axes="false"
            :hlines="[{ y: 0, color: '#1b1b1b' }]"
            :labels="[{ x: k + 1, y: hj[k] + hMax * 0.06, text: `h(${k + 1})`, color: GOLD, size: 13 }]"
          />
        </div>
        <div class="cap">how much of each part this one face needs: r = 16 numbers instead of {{ P }}</div>
        <div class="foot" :style="{ color: GOLD }">H is r × 300: one column per face</div>
      </div>
    </div>
    <div class="controls">
      <Knob v-model="j" :min="0" :max="299" :step="1" label="face j" :digits="0" :color="BLUE" />
      <Knob v-model="k" :min="0" :max="15" :step="1" label="part k" :digits="0" :color="PURPLE" />
    </div>
    <div class="credit">data: Olivetti faces, AT&amp;T Cambridge (shrunk to 32 × 32); NMF with r = 16</div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.4rem; height: 100%; min-height: 0; }
.top { text-align: center; }
.cols { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.6rem; min-height: 0; }
.col { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.3rem; min-height: 0; border-left: 1px solid #e3e5e8; padding-left: 1rem; }
.col:first-child { border-left: none; padding-left: 0; }
.h { text-align: center; font-weight: 600; font-size: 0.9rem; }
.pair { display: grid; grid-template-columns: 1fr auto 2rem; gap: 0.5rem; align-items: center; min-height: 0; }
.pair > :first-child { height: 7.5rem; }
.strip { height: 11rem; }
.arrow { color: #9aa0a6; font-size: 1.3rem; }
.bars { min-height: 0; }
.cap { text-align: center; color: #9aa0a6; font-size: 0.75rem; line-height: 1.35; }
.foot { text-align: center; font-size: 0.8rem; }
</style>
