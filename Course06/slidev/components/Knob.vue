<!-- One labelled slider. `log` makes it move in decades, which is how C and
     gamma are actually explored. -->
<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: number
    min: number
    max: number
    step?: number
    label?: string
    unit?: string
    log?: boolean
    digits?: number
    color?: string
    disabled?: boolean
  }>(),
  { step: 0, label: '', unit: '', log: false, digits: 2, color: '#1b1b1b', disabled: false },
)
const emit = defineEmits<{ 'update:modelValue': [number] }>()

const raw = computed(() =>
  props.log ? Math.log10(Math.max(props.modelValue, 1e-12)) : props.modelValue,
)
const bounds = computed(() =>
  props.log
    ? { lo: Math.log10(props.min), hi: Math.log10(props.max), st: props.step || 0.02 }
    : { lo: props.min, hi: props.max, st: props.step || (props.max - props.min) / 100 },
)
const shown = computed(() => {
  const v = props.modelValue
  if (props.log) {
    if (v >= 100) return v.toFixed(0)
    if (v >= 1) return v.toFixed(v % 1 === 0 ? 0 : 1)
    return v.toPrecision(2).replace(/0+$/, '').replace(/\.$/, '')
  }
  return v.toFixed(props.digits)
})

function onInput(e: Event) {
  const v = Number((e.target as HTMLInputElement).value)
  emit('update:modelValue', props.log ? 10 ** v : v)
}
</script>

<template>
  <label class="knob" :class="{ disabled }">
    <span v-if="label" class="knob-label" v-html="label" />
    <input
      type="range"
      :min="bounds.lo"
      :max="bounds.hi"
      :step="bounds.st"
      :value="raw"
      :disabled="disabled"
      :style="{ '--knob': color }"
      @input="onInput"
    />
    <span class="knob-value" :style="{ color }">{{ shown }}<span v-if="unit" class="knob-unit">{{ unit }}</span></span>
  </label>
</template>

<style scoped>
.knob {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.82rem;
  line-height: 1;
}
.knob.disabled { opacity: 0.4; }
input[type='range']:disabled { cursor: not-allowed; }
.knob-label { color: #4a4a4a; white-space: nowrap; }
.knob-value {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  min-width: 2.6rem;
  text-align: right;
}
.knob-unit { font-weight: 400; color: #9aa0a6; margin-left: 0.1rem; }
input[type='range'] {
  -webkit-appearance: none;
  appearance: none;
  height: 1.05rem;
  background: transparent;
  cursor: pointer;
  min-width: 3rem;
}
input[type='range']::-webkit-slider-runnable-track {
  height: 3px;
  border-radius: 3px;
  background: #d8dadd;
}
input[type='range']::-moz-range-track {
  height: 3px;
  border-radius: 3px;
  background: #d8dadd;
}
input[type='range']::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 0.85rem;
  height: 0.85rem;
  margin-top: -0.3rem;
  border-radius: 50%;
  background: var(--knob, #1b1b1b);
  border: 2px solid white;
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.15);
}
input[type='range']::-moz-range-thumb {
  width: 0.85rem;
  height: 0.85rem;
  border-radius: 50%;
  background: var(--knob, #1b1b1b);
  border: 2px solid white;
}
</style>
