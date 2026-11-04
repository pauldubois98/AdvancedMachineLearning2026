<!-- log_likelihood: L is a product of n numbers below 1, ℓ a sum. With more
     points L underflows a float; ℓ does not, and its argmax is the same. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { Rng } from '../lib/rng'
import { curve, sci } from '../lib/hist'
import { lognpdf, normals, npdf } from '../lib/stats'
import { GREEN, INK, RED } from '../lib/theme'

const n = ref(40)
const all = normals(new Rng(19), 2000, 2, 1)
const x = computed(() => all.slice(0, Math.round(n.value)))
// the product, computed exactly as a float64 would: no logs, no rescaling
const L = (m: number) => { let p = 1; for (const v of x.value) p *= npdf(v, m, 1); return p }
const ll = (m: number) => { let s = 0; for (const v of x.value) s += lognpdf(v, m, 1); return s }
const Lc = computed(() => curve(L, 0.6, 3.4, 400))
const llc = computed(() => curve(ll, 0.6, 3.4, 400))
const Lmax = computed(() => Math.max(...Lc.value.map((p) => p[1])))
const arg = (c: [number, number][]) => c.reduce((a, b) => (b[1] > a[1] ? b : a))[0]
const lmin = computed(() => Math.min(...llc.value.map((p) => p[1])))
const lmax = computed(() => Math.max(...llc.value.map((p) => p[1])))
const dead = computed(() => Lmax.value === 0)
</script>

<template>
  <div class="cmp top">
    <div class="setup"><b>Simulated:</b> n points from N(2, 1), the model N(θ, 1). Left, L(θ) computed as the plain product of n densities in 64-bit floats; right, ℓ(θ) as the sum of their logs.</div>
    <div class="r2">
      <LineChart :series="[{ points: Lc, color: RED }]" :x-domain="[0.6, 3.4]" :y-domain="[0, dead ? 1 : Lmax * 1.1]" :x-ticks="[1, 1.5, 2, 2.5, 3]" :y-ticks="[]" x-label="θ"
        :vlines="dead ? [] : [{ x: arg(Lc), color: INK, dash: '6,4' }]" :title="`L(θ): a product of ${Math.round(n)} terms`" :title-color="RED" />
      <LineChart :series="[{ points: llc, color: GREEN }]" :x-domain="[0.6, 3.4]" :y-domain="[lmin, lmax + (lmax - lmin) * 0.05]" :x-ticks="[1, 1.5, 2, 2.5, 3]" :y-ticks="[]" x-label="θ"
        :vlines="[{ x: arg(llc), color: INK, dash: '6,4' }]" :title="`ℓ(θ): a sum of ${Math.round(n)} terms`" :title-color="GREEN" />
    </div>
    <div class="foot" v-if="!dead">peak of L = <b :style="{ color: RED }">{{ sci(Lmax) }}</b> (a float stops at about 10⁻³⁰⁸) · peak of ℓ = <b :style="{ color: GREEN }">{{ lmax.toFixed(1) }}</b> · the argmax is the same</div>
    <div class="foot" v-else><b :style="{ color: RED }">L has underflowed: every product is exactly 0</b>, the argmax is lost · ℓ is still fine, peak <b :style="{ color: GREEN }">{{ lmax.toFixed(1) }}</b> at θ = {{ arg(llc).toFixed(2) }}</div>
    <div class="controls"><Knob v-model="n" :min="5" :max="2000" log :step="0.01" label="number of points n" :color="INK" /></div>
  </div>
</template>
