import { onBeforeUnmount, onMounted, ref, type Ref } from 'vue'

/** An svg stretched to its box with preserveAspectRatio="none" squashes its
 *  text (and turns its dots into ellipses). Instead, give it a viewBox with the
 *  box's own aspect ratio, so a unit is as long across as it is down: the
 *  height stays H0, so text keeps the height it had, and the width follows. */
export function useFitBox(el: Ref<Element | null>, W0: number, H0: number) {
  const W = ref(W0)
  const H = ref(H0)
  let ro: ResizeObserver | null = null
  function measure() {
    const box = el.value
    if (!box || !box.clientWidth || !box.clientHeight) return
    W.value = (H0 * box.clientWidth) / box.clientHeight
  }
  onMounted(() => {
    measure()
    ro = new ResizeObserver(measure)
    if (el.value) ro.observe(el.value)
  })
  onBeforeUnmount(() => ro?.disconnect())
  return { W, H }
}
