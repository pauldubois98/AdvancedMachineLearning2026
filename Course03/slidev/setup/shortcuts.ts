// `h` hides Slidev's navigation bar, and `h` again brings it back. On a tall
// window Slidev pins that bar over the bottom of the slide; style.css makes it
// appear only on hover, and this hides it completely.
import { defineShortcutsSetup } from '@slidev/types'

const KEY = 'aml-nav-hidden'

function apply(hidden: boolean) {
  document.documentElement.classList.toggle('nav-hidden', hidden)
  try { localStorage.setItem(KEY, hidden ? '1' : '0') } catch {}
}

try { apply(localStorage.getItem(KEY) === '1') } catch {}

export default defineShortcutsSetup((_nav, base) => [
  ...base,
  {
    name: 'toggle_nav',
    key: 'h',
    fn: () => apply(!document.documentElement.classList.contains('nav-hidden')),
  },
])
