<!-- sne_toy: the toy every step is drawn on. -->
<script setup lang="ts">
import { TOY, TOY_DOMAIN } from '../lib/data'
import { COMP, HIGH, LOW } from '../lib/theme'
const q = Array.from({ length: 9 }, (_, k) => ({ x: -1 + k / 4, y: 0.25, text: '?', color: LOW, size: 20 }))
</script>

<template>
  <div class="cmp">
    <div class="r2">
      <Plane :X="TOY.X" :colors="TOY.g.map((k) => COMP[k])" :size="5" :domain="TOY_DOMAIN" title="the data: 45 points in 2-D" :title-color="HIGH" />
      <LineChart :series="[{ points: [[-1.2, 0], [1.2, 0]], color: '#cccfd2', width: 2 }]" :labels="q" :axes="false"
        :x-domain="[-1.2, 1.2]" :y-domain="[-1, 1]" title="the map: 45 numbers on a line" :title-color="LOW" />
    </div>
    <div class="foot">Three groups (tight, wide, medium) in 2-D, mapped onto a line so that both can be drawn.<br>
      The colours are only for us: SNE never sees the groups.</div>
    <div />
  </div>
</template>
