// Small UI animations (task 081, docs/design.md 8 "Animácie (081)").
// Rules: only transform/opacity, nothing blocks content, no animation with
// prefers-reduced-motion: reduce. Every animation has a switch here: set it to
// false and the app falls back to the pre-081 behaviour (instant change).

export const MOTION = {
  /** Date panels (Akcie period, map day, calendar) slide up/down like the Filter panel */
  sheet: true,
  /** Heart pops (1 -> 1.3 -> 1) when turned on */
  heartPop: false, // off after 081 measurement: longest frame 66.7 ms (before max 33.4 ms)
  /** Pre teba: sparkle icon on the chip twinkles when turned on */
  forYouSparkle: false, // off after 081 measurement (Pre teba: 66.7 ms vs 33.4 ms)
  /** Pre teba: ✦ badges on visible cards pop in one after another */
  forYouBadges: false, // off after 081 measurement (Pre teba: 66.7 ms vs 33.4 ms)
  /** Cards, rows and buttons shrink to 0.97 while pressed */
  press: true,
  /** Count badge on the Filter button bumps when the number changes */
  filterBadge: true,
  /** Akcie count line slides in from below when it changes */
  countSlide: true,
  /** Bottom bar: pink pill moves to the new tab, its icon pops */
  navPill: true,
  /** Map: pins drop into place on map open / day / filter / favourites change */
  pinDrop: true,
  /** Idem (bookmark) pops + small burst of dots when turned on */
  goingBurst: true,
  /** Short vibration on heart / Idem (independent of reduced motion) */
  vibrate: true,
}

export type MotionKey = keyof typeof MOTION

/** Debug: `?motionoff=heartPop,press` (or `?motionoff=all`) in the URL switches
 * animations off for this page load, e.g. to compare on a phone. */
export function applyMotionOffParam(search: string): void {
  const m = /[?&]motionoff=([^&#]*)/.exec(search)
  if (!m) return
  const keys = decodeURIComponent(m[1]!).split(',').map(k => k.trim())
  for (const k of Object.keys(MOTION) as MotionKey[]) {
    if (keys.includes('all') || keys.includes(k)) MOTION[k] = false
  }
}
try { if (typeof location !== 'undefined') applyMotionOffParam(location.search) } catch { /* ignore */ }

export function prefersReducedMotion(): boolean {
  try { return window.matchMedia('(prefers-reduced-motion: reduce)').matches } catch { return false }
}

/** True when the animation is switched on and the user does not prefer reduced motion. */
export function motionOn(key: MotionKey): boolean {
  return MOTION[key] && !prefersReducedMotion()
}

/** Short haptic tick; silently does nothing where unsupported. */
export function vibrate(ms = 12): void {
  if (!MOTION.vibrate) return
  try {
    const nav = typeof navigator !== 'undefined' ? navigator : undefined
    if (nav && typeof nav.vibrate === 'function') nav.vibrate(ms)
  } catch { /* never fail */ }
}

/** Runs a Web Animations API animation if the switch is on; never throws. */
export function play(key: MotionKey, el: Element | null | undefined, keyframes: Keyframe[], options: KeyframeAnimationOptions): Animation | null {
  if (!el || !motionOn(key)) return null
  try {
    if (typeof (el as HTMLElement).animate !== 'function') return null
    return (el as HTMLElement).animate(keyframes, options)
  } catch { return null }
}

export const POP_KEYFRAMES: Keyframe[] = [
  { transform: 'scale(1)' }, { transform: 'scale(1.3)' }, { transform: 'scale(1)' },
]

/** Heart turned on: pop + vibration. Call only from the tap handler. */
export function heartPop(el: Element | null | undefined): void {
  vibrate(12)
  play('heartPop', el, POP_KEYFRAMES, { duration: 250, easing: 'cubic-bezier(.3,.7,.4,1)' })
}

/** Class name for the press effect (CSS in styles/global.css), '' when switched off. */
export function pressClass(extra = ''): string {
  const base = MOTION.press ? 'm-press' : ''
  return [base, extra].filter(Boolean).join(' ')
}

/** Delays for staggered items: first `max` items get i*step ms, the rest 0 (shown at once). */
export function staggerDelays(count: number, max: number, step: number): number[] {
  return Array.from({ length: count }, (_, i) => (i < max ? i * step : -1))
}

/** Pin drop delay by distance from the screen centre: 0 at the centre, `maxDelay` at the corner. */
export function pinDropDelay(x: number, y: number, width: number, height: number, maxDelay = 120): number {
  const cx = width / 2
  const cy = height / 2
  const maxD = Math.hypot(cx, cy) || 1
  const d = Math.min(1, Math.hypot(x - cx, y - cy) / maxD)
  return Math.round(d * maxDelay)
}

/** Idem turned on: the button pops, a few dots burst around it (≤ 400 ms), vibration.
 * Dots live in a fixed layer on <body> so React's DOM is not touched. */
export function goingBurst(el: HTMLElement | null | undefined, dots = 8): void {
  vibrate(12)
  if (!el || !motionOn('goingBurst')) return
  play('goingBurst', el, POP_KEYFRAMES, { duration: 250, easing: 'cubic-bezier(.3,.7,.4,1)' })
  try {
    const r = el.getBoundingClientRect()
    const layer = document.createElement('div')
    layer.setAttribute('aria-hidden', 'true')
    layer.style.cssText = `position:fixed;left:${r.left + r.width / 2}px;top:${r.top + r.height / 2}px;width:0;height:0;pointer-events:none;z-index:200`
    for (let i = 0; i < dots; i++) {
      const d = document.createElement('span')
      d.className = 'm-burst-dot'
      d.style.setProperty('--a', `${Math.round((360 / dots) * i)}deg`)
      layer.appendChild(d)
    }
    document.body.appendChild(layer)
    setTimeout(() => layer.remove(), 420)
  } catch { /* never fail */ }
}

/** Press effect for `.m-press` elements (task 081): one delegated listener set.
 * The class is removed when the finger moves (scroll / swipe), so scrolling
 * never leaves a card pressed. Taps on `.m-press-stop` (e.g. a heart inside a
 * row) do not press the row. Shown at least ~90 ms so quick taps are visible. */
export function installPressHandler(): void {
  if (typeof document === 'undefined' || !MOTION.press) return
  let el: HTMLElement | null = null
  let x = 0, y = 0, t = 0
  const release = (immediate: boolean) => {
    const cur = el
    if (!cur) return
    el = null
    const wait = immediate ? 0 : Math.max(0, 90 - (performance.now() - t))
    if (wait === 0) cur.classList.remove('is-pressed')
    else setTimeout(() => cur.classList.remove('is-pressed'), wait)
  }
  document.addEventListener('pointerdown', e => {
    release(true)
    if (prefersReducedMotion()) return
    const target = e.target as Element | null
    const p = target?.closest?.('.m-press') as HTMLElement | null
    if (!p) return
    const stop = target?.closest?.('.m-press-stop')
    if (stop && p.contains(stop)) return
    el = p; x = e.clientX; y = e.clientY; t = performance.now()
    p.classList.add('is-pressed')
  }, { passive: true })
  document.addEventListener('pointermove', e => {
    if (el && Math.hypot(e.clientX - x, e.clientY - y) > 8) release(true)
  }, { passive: true })
  document.addEventListener('pointerup', () => release(false), { passive: true })
  document.addEventListener('pointercancel', () => release(true), { passive: true })
  document.addEventListener('scroll', () => release(true), { passive: true, capture: true })
}
