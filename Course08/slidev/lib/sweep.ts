import { onBeforeUnmount, onMounted, ref, watch, type Ref, type WatchSource } from 'vue'

/** Fill fn(v) for every v of `values`, one per animation frame, so a curve
 *  that needs dozens of refits grows on screen instead of freezing the
 *  slide. Restarts from scratch whenever a `deps` source changes. */
export function useSweep<T>(values: () => number[], fn: (v: number) => T, deps: WatchSource[] = []): Ref<(T | null)[]> {
  const out = ref<(T | null)[]>([]) as Ref<(T | null)[]>
  let run = 0
  let timer = 0
  function start() {
    const id = ++run
    const vs = values()
    out.value = vs.map(() => null)
    let i = 0
    const step = () => {
      if (id !== run || i >= vs.length) return
      const t0 = performance.now()
      // a few at a time while the frame budget lasts
      while (i < vs.length && performance.now() - t0 < 12) {
        const next = [...out.value]
        next[i] = fn(vs[i])
        out.value = next
        i++
      }
      timer = window.setTimeout(step, 0)
    }
    timer = window.setTimeout(step, 30)
  }
  onMounted(start)
  if (deps.length) watch(deps, start)
  onBeforeUnmount(() => { run++; clearTimeout(timer) })
  return out
}
