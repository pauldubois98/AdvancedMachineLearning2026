<!-- A formula inside a component. The slide markdown gets KaTeX for free, but
     a Vue template is never markdown-parsed, so the few formulas that live
     next to a slider are rendered here instead. -->
<script setup lang="ts">
import { computed } from 'vue'
import katex from 'katex'

const props = withDefaults(defineProps<{ formula: string; display?: boolean }>(), {
  display: false,
})
const html = computed(() =>
  katex.renderToString(props.formula, {
    displayMode: props.display,
    throwOnError: false,
    output: 'html',
  }),
)
</script>

<template>
  <span class="tex" :class="{ display }" v-html="html" />
</template>

<style scoped>
.tex.display { display: block; text-align: center; }
</style>
