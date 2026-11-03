<!-- cv_cost: the number of fits multiplies. The three rows of the printed
     table, plus a calculator: folds, values per knob, knobs, repeats, and the
     time one fit takes. -->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { BLUE, GOLD, PURPLE, RED } from '../lib/theme'

const K = ref(10)
const vals = ref(10)
const knobs = ref(2)
const reps = ref(1)
const secs = ref(30)
const fits = computed(() => K.value * vals.value ** knobs.value * reps.value)
const time = computed(() => {
  const s = fits.value * secs.value
  if (s < 120) return `${s.toFixed(0)} s`
  if (s < 7200) return `${(s / 60).toFixed(0)} min`
  if (s < 3 * 86400) return `${(s / 3600).toFixed(1)} h`
  if (s < 2 * 365 * 86400) return `${(s / 86400).toFixed(0)} days`
  return `${(s / 86400 / 365).toFixed(0)} years`
})
const n = (v: number) => v.toLocaleString('en-US').replace(/,/g, ' ')
</script>

<template>
  <div class="wrap">
    <div class="eq">number of fits &nbsp;=&nbsp; <Tex formula="K" /> folds &nbsp;×&nbsp; candidate models &nbsp;×&nbsp; repeats</div>
    <table class="plain cost">
      <tbody>
      <tr><th></th><th>arithmetic</th><th style="text-align: right">fits</th></tr>
      <tr><td :style="{ color: BLUE }">one knob, ten orders, <Tex formula="K = 10" /></td><td class="m">10 × 10</td><td class="f" :style="{ color: BLUE }">100</td></tr>
      <tr><td :style="{ color: GOLD }">two knobs, a 10 × 10 grid</td><td class="m">10 × 100</td><td class="f" :style="{ color: GOLD }">1 000</td></tr>
      <tr><td :style="{ color: PURPLE }">the same, five repeated partitions</td><td class="m">10 × 100 × 5</td><td class="f" :style="{ color: PURPLE }">5 000</td></tr>
      <tr class="yours">
        <td :style="{ color: RED }">yours: {{ knobs }} knob{{ knobs > 1 ? 's' : '' }}, {{ vals }} values each</td>
        <td class="m">{{ K }} × {{ vals }}<sup v-if="knobs > 1">{{ knobs }}</sup> × {{ reps }}</td>
        <td class="f" :style="{ color: RED }">{{ n(fits) }}</td>
      </tr>
    </tbody>
    </table>
    <div class="time">at {{ secs }} s per fit: <b :style="{ color: RED }">{{ time }}</b> of computing</div>
    <div class="controls">
      <Knob v-model="K" :min="2" :max="20" :step="1" :digits="0" label="folds K" />
      <Knob v-model="vals" :min="2" :max="20" :step="1" :digits="0" label="values per knob" />
      <Knob v-model="knobs" :min="1" :max="6" :step="1" :digits="0" label="knobs" />
      <Knob v-model="reps" :min="1" :max="10" :step="1" :digits="0" label="repeats" />
      <Knob v-model="secs" :min="1" :max="3600" log label="seconds per fit" />
    </div>
  </div>
</template>

<style scoped>
.wrap { display: grid; grid-template-rows: auto 1fr auto auto; gap: 0.8rem; height: 100%; min-height: 0; align-content: center; }
.eq { text-align: center; font-size: 1.35rem; }
.cost { width: 88%; margin: 0 auto; font-size: 0.95rem; }
.cost .m { color: #9aa0a6; }
.cost .f { text-align: right; font-weight: 700; font-variant-numeric: tabular-nums; }
.yours td { border-top: 2px solid #cccfd2; }
.time { text-align: center; font-size: 1rem; }
.controls > .knob { min-width: 9rem; }
</style>
