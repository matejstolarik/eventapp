import { describe, it, expect, afterEach, vi } from 'vitest'
import { MOTION, applyMotionOffParam, motionOn, prefersReducedMotion, vibrate, play, heartPop, goingBurst, pressClass, staggerDelays, pinDropDelay, type MotionKey } from './motion'

const g = globalThis as unknown as { window?: unknown; navigator?: unknown }

function setReduced(reduce: boolean) {
  g.window = { matchMedia: (q: string) => ({ matches: reduce && q.includes('reduce') }) }
}

function fakeEl() {
  return { animate: vi.fn(() => ({}) as Animation), getBoundingClientRect: () => ({ left: 0, top: 0, width: 40, height: 40 }) }
}

const saved = { ...MOTION }
afterEach(() => {
  Object.assign(MOTION, saved)
  delete g.window
  vi.unstubAllGlobals()
})

describe('motion switches (task 081)', () => {
  it('every animation is on by default and has a switch', () => {
    for (const k of Object.keys(MOTION) as MotionKey[]) expect(typeof MOTION[k]).toBe('boolean')
  })

  it('motionOn is false with prefers-reduced-motion: reduce', () => {
    setReduced(true)
    expect(prefersReducedMotion()).toBe(true)
    for (const k of Object.keys(MOTION) as MotionKey[]) expect(motionOn(k)).toBe(false)
  })

  it('motionOn follows the switch without reduced motion', () => {
    setReduced(false)
    MOTION.heartPop = true
    expect(motionOn('heartPop')).toBe(true)
    MOTION.heartPop = false
    expect(motionOn('heartPop')).toBe(false)
  })

  it('no window (tests / SSR) means no reduced motion, no crash', () => {
    expect(prefersReducedMotion()).toBe(false)
  })
})

describe('play / heartPop / goingBurst', () => {
  it('does not animate with reduced motion', () => {
    setReduced(true)
    const el = fakeEl()
    expect(play('heartPop', el as unknown as Element, [], { duration: 10 })).toBeNull()
    heartPop(el as unknown as Element)
    goingBurst(el as unknown as HTMLElement)
    expect(el.animate).not.toHaveBeenCalled()
  })

  it('does not animate when the switch is off', () => {
    setReduced(false)
    MOTION.heartPop = false
    const el = fakeEl()
    heartPop(el as unknown as Element)
    expect(el.animate).not.toHaveBeenCalled()
  })

  it('heart pop is scale 1 -> 1.3 -> 1 in ~250 ms', () => {
    setReduced(false)
    MOTION.heartPop = true
    const el = fakeEl()
    heartPop(el as unknown as Element)
    expect(el.animate).toHaveBeenCalledTimes(1)
    const [frames, opts] = el.animate.mock.calls[0] as unknown as [Keyframe[], KeyframeAnimationOptions]
    expect(frames.map(f => f.transform)).toEqual(['scale(1)', 'scale(1.3)', 'scale(1)'])
    expect(opts.duration).toBeLessThanOrEqual(250)
  })

  it('never throws for missing elements or animate()', () => {
    setReduced(false)
    expect(play('heartPop', null, [], {})).toBeNull()
    expect(play('heartPop', {} as Element, [], {})).toBeNull()
    expect(() => heartPop(null)).not.toThrow()
  })
})

describe('vibrate', () => {
  it('works without navigator.vibrate', () => {
    vi.stubGlobal('navigator', {})
    expect(() => vibrate()).not.toThrow()
  })

  it('vibrates briefly also with reduced motion', () => {
    setReduced(true)
    const v = vi.fn()
    vi.stubGlobal('navigator', { vibrate: v })
    heartPop(fakeEl() as unknown as Element)
    expect(v).toHaveBeenCalledTimes(1)
    const ms = v.mock.calls[0]![0] as number
    expect(ms).toBeGreaterThanOrEqual(10)
    expect(ms).toBeLessThanOrEqual(15)
  })

  it('swallows errors from navigator.vibrate', () => {
    vi.stubGlobal('navigator', { vibrate: () => { throw new Error('blocked') } })
    expect(() => vibrate()).not.toThrow()
  })

  it('respects the vibrate switch', () => {
    MOTION.vibrate = false
    const v = vi.fn()
    vi.stubGlobal('navigator', { vibrate: v })
    vibrate()
    expect(v).not.toHaveBeenCalled()
  })
})

describe('helpers', () => {
  it('?motionoff= switches animations off', () => {
    applyMotionOffParam('?motionoff=heartPop,press')
    expect(MOTION.heartPop).toBe(false)
    expect(MOTION.press).toBe(false)
    expect(MOTION.pinDrop).toBe(true)
    applyMotionOffParam('?x=1&motionoff=all')
    for (const k of Object.keys(MOTION) as MotionKey[]) expect(MOTION[k]).toBe(false)
  })

  it('pressClass is empty when the switch is off', () => {
    expect(pressClass()).toBe('m-press')
    MOTION.press = false
    expect(pressClass()).toBe('')
  })

  it('stagger: first 12 items within 300 ms, the rest at once', () => {
    const d = staggerDelays(20, 12, 10)
    expect(d.slice(0, 12).every(x => x >= 0)).toBe(true)
    expect(Math.max(...d) + 180).toBeLessThanOrEqual(300)
    expect(d.slice(12).every(x => x === -1)).toBe(true)
  })

  it('pin drop delay: 0 in the centre, ≤ 120 ms at the corner (with 180 ms drop ≤ 300 ms)', () => {
    expect(pinDropDelay(195, 422, 390, 844)).toBe(0)
    expect(pinDropDelay(0, 0, 390, 844)).toBe(120)
    expect(pinDropDelay(-500, -500, 390, 844)).toBe(120)
    expect(pinDropDelay(100, 200, 390, 844)).toBeGreaterThan(0)
  })
})
