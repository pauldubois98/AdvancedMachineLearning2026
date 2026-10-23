import { onBeforeUnmount, ref, shallowRef, watch, type Ref } from 'vue'

/**
 * An iterative fit that runs while you watch: `make` builds a fresh state
 * whenever its inputs change, `step` advances it one pass, and the passes run
 * a few at a time inside animation frames, so the slide stays responsive and
 * the loss curve grows live. Nothing runs while the slide is hidden.
 */
export function useRun<S>(opts: {
  /** build the starting state */
  make: () => S
  /** the inputs of `make`: the run restarts whenever this changes */
  key: () => unknown
  step: (s: S) => void
  /** the number recorded after every pass, e.g. the loss */
  score?: (s: S) => number
  passes: () => number
  /** how many passes between two recorded scores */
  every?: number
  el: Ref<Element | null>
  budget?: number
}) {
  const state = shallowRef<S>(null as unknown as S)
  const pass = ref(0)
  const hist = shallowRef<[number, number][]>([])
  const tick = ref(0)
  let raf = 0
  let gen = 0

  function restart() {
    gen++
    state.value = opts.make()
    pass.value = 0
    hist.value = opts.score ? [[0, opts.score(state.value)]] : []
    tick.value++
  }

  function frame() {
    raf = requestAnimationFrame(frame)
    const box = opts.el.value as HTMLElement | null
    if (!box || !box.offsetParent || !box.clientWidth) return
    const target = opts.passes()
    if (pass.value >= target) return
    const t0 = performance.now()
    const g = gen
    const h = hist.value.slice()
    while (pass.value < target && performance.now() - t0 < (opts.budget ?? 14)) {
      opts.step(state.value)
      pass.value++
      if (opts.score && (pass.value % (opts.every ?? 1) === 0 || pass.value === target)) {
        h.push([pass.value, opts.score(state.value)])
      }
    }
    if (g !== gen) return
    hist.value = h
    tick.value++
  }

  watch(() => JSON.stringify(opts.key()), () => restart())

  // built at once, so the template can read `state` from the first render
  restart()
  raf = requestAnimationFrame(frame)
  onBeforeUnmount(() => cancelAnimationFrame(raf))
  return { state, pass, hist, tick, restart }
}
